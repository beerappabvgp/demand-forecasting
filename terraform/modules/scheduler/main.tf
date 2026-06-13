############################################################
# Data: zip the Lambda code for deployment
############################################################
data "archive_file" "scheduler_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_scheduler.py"
  output_path = "${path.module}/scheduler.zip"
}

############################################################
# IAM Role for Lambda
############################################################
resource "aws_iam_role" "scheduler_lambda" {
  name = "${var.project_name}-scheduler-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "scheduler_lambda" {
  name = "${var.project_name}-scheduler-lambda-policy"
  role = aws_iam_role.scheduler_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # CloudWatch Logs (Lambda execution logs)
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      # ECS: start/stop service
      {
        Effect   = "Allow"
        Action   = ["ecs:UpdateService", "ecs:DescribeServices"]
        Resource = "*"
      },
      # EC2: manage NAT Gateway and routes
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNatGateway",
          "ec2:DeleteNatGateway",
          "ec2:DescribeNatGateways",
          "ec2:CreateRoute",
          "ec2:DeleteRoute",
          "ec2:ReplaceRoute",
          "ec2:DescribeRouteTables",
          "ec2:CreateTags"
        ]
        Resource = "*"
      },
      # SSM: read/write NAT GW ID and EIP
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:PutParameter"
        ]
        Resource = "arn:aws:ssm:${var.aws_region}:*:parameter/${var.project_name}/*"
      }
    ]
  })
}

############################################################
# Lambda Function
############################################################
resource "aws_lambda_function" "scheduler" {
  function_name    = "${var.project_name}-resource-scheduler"
  role             = aws_iam_role.scheduler_lambda.arn
  handler          = "lambda_scheduler.handler"
  runtime          = "python3.12"
  filename         = data.archive_file.scheduler_zip.output_path
  source_code_hash = data.archive_file.scheduler_zip.output_base64sha256
  timeout          = 300  # 5 minutes — NAT GW creation takes 60-90s

  environment {
    variables = {
      AWS_REGION_NAME  = var.aws_region
      ECS_CLUSTER      = var.ecs_cluster_name
      ECS_SERVICE      = var.ecs_service_name
      PUBLIC_SUBNET_ID = var.public_subnet_id
      ROUTE_TABLE_ID   = var.route_table_id
      SSM_NAT_GW_ID    = "/${var.project_name}/nat-gateway-id"
      SSM_EIP_ALLOC_ID = "/${var.project_name}/eip-allocation-id"
    }
  }
}

############################################################
# SSM Parameters: initial values
############################################################
resource "aws_ssm_parameter" "nat_gw_id" {
  name  = "/${var.project_name}/nat-gateway-id"
  type  = "String"
  value = var.initial_nat_gw_id   # Seeded on first apply; Lambda keeps it updated
  lifecycle {
    # Lambda will overwrite this — don't let Terraform reset it on every apply
    ignore_changes = [value]
  }
}

resource "aws_ssm_parameter" "eip_alloc_id" {
  name  = "/${var.project_name}/eip-allocation-id"
  type  = "String"
  value = var.nat_eip_allocation_id  # The EIP to reuse every morning
  lifecycle {
    ignore_changes = [value]
  }
}

############################################################
# EventBridge Rules
############################################################

# STOP: 6:00 PM IST = 12:30 PM UTC, Mon–Fri
resource "aws_cloudwatch_event_rule" "stop_schedule" {
  name                = "${var.project_name}-stop-schedule"
  description         = "Stop all resources at 6 PM IST (Mon-Fri)"
  schedule_expression = "cron(30 12 ? * MON-FRI *)"
}

# START: 9:00 AM IST = 3:30 AM UTC, Mon–Fri
resource "aws_cloudwatch_event_rule" "start_schedule" {
  name                = "${var.project_name}-start-schedule"
  description         = "Start all resources at 9 AM IST (Mon-Fri)"
  schedule_expression = "cron(30 3 ? * MON-FRI *)"
}

############################################################
# EventBridge → Lambda Targets
############################################################
resource "aws_cloudwatch_event_target" "stop_target" {
  rule = aws_cloudwatch_event_rule.stop_schedule.name
  arn  = aws_lambda_function.scheduler.arn
  input = jsonencode({ action = "stop" })
}

resource "aws_cloudwatch_event_target" "start_target" {
  rule = aws_cloudwatch_event_rule.start_schedule.name
  arn  = aws_lambda_function.scheduler.arn
  input = jsonencode({ action = "start" })
}

############################################################
# Allow EventBridge to invoke Lambda
############################################################
resource "aws_lambda_permission" "allow_stop_event" {
  statement_id  = "AllowEventBridgeStop"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scheduler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.stop_schedule.arn
}

resource "aws_lambda_permission" "allow_start_event" {
  statement_id  = "AllowEventBridgeStart"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.scheduler.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.start_schedule.arn
}

############################################################
# CloudWatch Log Group for Lambda
############################################################
resource "aws_cloudwatch_log_group" "scheduler_logs" {
  name              = "/aws/lambda/${aws_lambda_function.scheduler.function_name}"
  retention_in_days = 7
}
