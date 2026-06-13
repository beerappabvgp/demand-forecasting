import boto3
import os
import time

def handler(event, context):
    """
    Entry point. EventBridge passes {"action": "start"} or {"action": "stop"}.
    """
    action = event.get('action', '')
    print(f"Scheduler triggered with action: {action}")

    if action == 'stop':
        stop_resources()
    elif action == 'start':
        start_resources()
    else:
        raise ValueError(f"Unknown action: '{action}'. Must be 'start' or 'stop'.")


# ─────────────────────────────────────────────────────────────────
# STOP: ECS → NAT Gateway → Route
# ─────────────────────────────────────────────────────────────────
def stop_resources():
    ecs = boto3.client('ecs', region_name=os.environ['AWS_REGION_NAME'])
    ec2 = boto3.client('ec2',  region_name=os.environ['AWS_REGION_NAME'])
    ssm = boto3.client('ssm',  region_name=os.environ['AWS_REGION_NAME'])

    cluster        = os.environ['ECS_CLUSTER']
    service        = os.environ['ECS_SERVICE']
    route_table_id = os.environ['ROUTE_TABLE_ID']
    ssm_nat_gw_key = os.environ['SSM_NAT_GW_ID']
    ssm_eip_key    = os.environ['SSM_EIP_ALLOC_ID']

    # 1. Scale ECS to 0 first so tasks can gracefully shut down
    print("Stopping ECS service (desiredCount=0)...")
    ecs.update_service(cluster=cluster, service=service, desiredCount=0)
    print("ECS service stopped.")

    # 2. Get current NAT GW ID from SSM
    try:
        nat_gw_id = ssm.get_parameter(Name=ssm_nat_gw_key)['Parameter']['Value']
        if nat_gw_id == 'deleted' or not nat_gw_id:
            print("NAT Gateway already deleted, skipping.")
            return
    except ssm.exceptions.ParameterNotFound:
        print("SSM parameter for NAT GW not found, skipping NAT GW deletion.")
        return

    # 3. Describe NAT GW to get EIP allocation ID before we delete it
    nat_gws = ec2.describe_nat_gateways(NatGatewayIds=[nat_gw_id])['NatGateways']
    if not nat_gws or nat_gws[0]['State'] not in ('available', 'pending'):
        print(f"NAT Gateway {nat_gw_id} is not in a deletable state, skipping.")
        ssm.put_parameter(Name=ssm_nat_gw_key, Value='deleted', Type='String', Overwrite=True)
        return

    eip_alloc_id = nat_gws[0]['NatGatewayAddresses'][0]['AllocationId']
    print(f"Saving EIP allocation ID {eip_alloc_id} to SSM for reuse tomorrow...")
    ssm.put_parameter(Name=ssm_eip_key, Value=eip_alloc_id, Type='String', Overwrite=True)

    # 4. Remove the route pointing to this NAT GW so route table is clean
    print(f"Removing 0.0.0.0/0 route from route table {route_table_id}...")
    try:
        ec2.delete_route(RouteTableId=route_table_id, DestinationCidrBlock='0.0.0.0/0')
        print("Route removed.")
    except Exception as e:
        print(f"Route removal skipped (may already be gone): {e}")

    # 5. Delete NAT Gateway
    print(f"Deleting NAT Gateway {nat_gw_id}...")
    ec2.delete_nat_gateway(NatGatewayId=nat_gw_id)

    # 6. Update SSM so start() knows it needs to create a new one
    ssm.put_parameter(Name=ssm_nat_gw_key, Value='deleted', Type='String', Overwrite=True)
    print("NAT Gateway deletion initiated. All resources stopped!")


# ─────────────────────────────────────────────────────────────────
# START: NAT Gateway → Route → ECS
# ─────────────────────────────────────────────────────────────────
def start_resources():
    ecs = boto3.client('ecs', region_name=os.environ['AWS_REGION_NAME'])
    ec2 = boto3.client('ec2',  region_name=os.environ['AWS_REGION_NAME'])
    ssm = boto3.client('ssm',  region_name=os.environ['AWS_REGION_NAME'])

    cluster        = os.environ['ECS_CLUSTER']
    service        = os.environ['ECS_SERVICE']
    public_subnet  = os.environ['PUBLIC_SUBNET_ID']
    route_table_id = os.environ['ROUTE_TABLE_ID']
    ssm_nat_gw_key = os.environ['SSM_NAT_GW_ID']
    ssm_eip_key    = os.environ['SSM_EIP_ALLOC_ID']

    # 1. Get the EIP to reuse from SSM
    eip_alloc_id = ssm.get_parameter(Name=ssm_eip_key)['Parameter']['Value']
    print(f"Using saved EIP: {eip_alloc_id}")

    # 2. Create a new NAT Gateway with the same EIP
    print(f"Creating NAT Gateway in subnet {public_subnet}...")
    response = ec2.create_nat_gateway(
        SubnetId=public_subnet,
        AllocationId=eip_alloc_id,
        TagSpecifications=[{
            'ResourceType': 'natgateway',
            'Tags': [
                {'Key': 'Name',    'Value': 'demand-forecasting-nat'},
                {'Key': 'Project', 'Value': 'demand-forecasting'}
            ]
        }]
    )
    nat_gw_id = response['NatGateway']['NatGatewayId']
    print(f"NAT Gateway created: {nat_gw_id}. Waiting for it to become available...")

    # Store ID immediately in case Lambda times out on retries
    ssm.put_parameter(Name=ssm_nat_gw_key, Value=nat_gw_id, Type='String', Overwrite=True)

    # 3. Poll until NAT GW is available (usually 60–90 seconds)
    for attempt in range(24):   # 24 × 10s = 4 minutes max
        time.sleep(10)
        nat_gw = ec2.describe_nat_gateways(NatGatewayIds=[nat_gw_id])['NatGateways'][0]
        state  = nat_gw['State']
        print(f"  Attempt {attempt+1}: NAT Gateway state = {state}")
        if state == 'available':
            break
        elif state == 'failed':
            raise RuntimeError("NAT Gateway creation failed! Check AWS console for details.")
    else:
        raise TimeoutError("NAT Gateway did not become available within 4 minutes.")

    # 4. Add route: 0.0.0.0/0 → new NAT GW
    print(f"Updating route table {route_table_id}...")
    try:
        ec2.create_route(
            RouteTableId=route_table_id,
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=nat_gw_id
        )
        print("Route created.")
    except ec2.exceptions.from_code('RouteAlreadyExists'):
        ec2.replace_route(
            RouteTableId=route_table_id,
            DestinationCidrBlock='0.0.0.0/0',
            NatGatewayId=nat_gw_id
        )
        print("Route replaced (existing route updated).")
    except Exception as e:
        # boto3 may use a different exception for this
        if 'RouteAlreadyExists' in str(e):
            ec2.replace_route(
                RouteTableId=route_table_id,
                DestinationCidrBlock='0.0.0.0/0',
                NatGatewayId=nat_gw_id
            )
            print("Route replaced.")
        else:
            raise

    # 5. Start ECS service
    print("Starting ECS service (desiredCount=1)...")
    ecs.update_service(cluster=cluster, service=service, desiredCount=1)
    print("ECS service started. All resources are running!")
