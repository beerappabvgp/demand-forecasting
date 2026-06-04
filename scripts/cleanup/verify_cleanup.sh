#!/bin/bash

# ============================================================
# VERIFICATION SCRIPT - Confirms all AWS resources are deleted
# ============================================================
# Run this independently at any time to check what is still running.
# Usage: bash scripts/cleanup/verify_cleanup.sh
# ============================================================

REGION="ap-south-1"
PASS="✅"
FAIL="❌"
WARN="⚠️ "

echo ""
echo "============================================================"
echo "  AWS RESOURCE VERIFICATION REPORT"
echo "  Region: $REGION"
echo "  Time:   $(date)"
echo "============================================================"

ISSUES=0

# --- VPC ---
echo ""
echo "--- VPC & Networking ---"
VPC_COUNT=$(aws ec2 describe-vpcs \
    --region $REGION \
    --filters "Name=tag:Project,Values=demand-forecasting" \
    --query 'length(Vpcs)' --output text 2>/dev/null)
if [ "$VPC_COUNT" = "0" ] || [ -z "$VPC_COUNT" ]; then
    echo "  $PASS VPC: None found (deleted)"
else
    echo "  $FAIL VPC: $VPC_COUNT still exist! Run terraform destroy."
    ISSUES=$((ISSUES+1))
fi

NAT_COUNT=$(aws ec2 describe-nat-gateways \
    --region $REGION \
    --filter "Name=state,Values=available,pending" \
    --query 'length(NatGateways)' --output text 2>/dev/null)
if [ "$NAT_COUNT" = "0" ] || [ -z "$NAT_COUNT" ]; then
    echo "  $PASS NAT Gateway: None running (most expensive resource - confirmed stopped)"
else
    echo "  $FAIL NAT Gateway: $NAT_COUNT still running! Billing ~\$0.045/hr"
    ISSUES=$((ISSUES+1))
fi

EIP_COUNT=$(aws ec2 describe-addresses \
    --region $REGION \
    --query 'length(Addresses)' --output text 2>/dev/null)
if [ "$EIP_COUNT" = "0" ] || [ -z "$EIP_COUNT" ]; then
    echo "  $PASS Elastic IP: None allocated (deleted)"
else
    echo "  $FAIL Elastic IP: $EIP_COUNT still allocated! Costs \$0.005/hr when unattached."
    ISSUES=$((ISSUES+1))
fi

# --- S3 Buckets ---
echo ""
echo "--- S3 Buckets ---"
for BUCKET in demand-forecasting-production-bronze-3lhyuk demand-forecasting-production-silver-3lhyuk demand-forecasting-production-mlflow-3lhyuk; do
    if aws s3 ls s3://$BUCKET --region $REGION > /dev/null 2>&1; then
        SIZE=$(aws s3 ls s3://$BUCKET --recursive --human-readable --summarize --region $REGION 2>/dev/null | grep "Total Size" | awk '{print $3, $4}')
        echo "  $WARN S3: s3://$BUCKET still exists (Size: $SIZE)"
        ISSUES=$((ISSUES+1))
    else
        echo "  $PASS S3: s3://$BUCKET deleted"
    fi
done

# --- ECR ---
echo ""
echo "--- ECR (Container Registry) ---"
ECR_COUNT=$(aws ecr describe-repositories \
    --region $REGION \
    --query 'length(repositories)' --output text 2>/dev/null)
if [ "$ECR_COUNT" = "0" ] || [ -z "$ECR_COUNT" ]; then
    echo "  $PASS ECR: No repositories found (deleted)"
else
    echo "  $WARN ECR: $ECR_COUNT repositories still exist (minimal cost per GB stored)"
    ISSUES=$((ISSUES+1))
fi

# --- IAM Roles ---
echo ""
echo "--- IAM Roles ---"
for ROLE in demand-forecasting-glue-service-role demand-forecasting-sagemaker-execution-role; do
    EXISTS=$(aws iam get-role --role-name $ROLE --query 'Role.RoleName' --output text 2>/dev/null || echo "")
    if [ -z "$EXISTS" ]; then
        echo "  $PASS IAM Role: $ROLE deleted"
    else
        echo "  $WARN IAM Role: $ROLE still exists (no cost, but cleanup recommended)"
        ISSUES=$((ISSUES+1))
    fi
done

# --- Glue Jobs ---
echo ""
echo "--- AWS Glue ---"
GLUE_JOB=$(aws glue get-job --job-name demand-forecasting-etl-bronze-to-silver --region $REGION --query 'Job.Name' --output text 2>/dev/null || echo "")
if [ -z "$GLUE_JOB" ]; then
    echo "  $PASS Glue Job: Deleted"
else
    echo "  $WARN Glue Job: demand-forecasting-etl-bronze-to-silver still exists (no cost when idle)"
    ISSUES=$((ISSUES+1))
fi

# --- SageMaker Training Jobs (Active) ---
echo ""
echo "--- SageMaker ---"
ACTIVE_JOBS=$(aws sagemaker list-training-jobs \
    --region $REGION \
    --status-equals InProgress \
    --query 'length(TrainingJobSummaries)' --output text 2>/dev/null)
if [ "$ACTIVE_JOBS" = "0" ] || [ -z "$ACTIVE_JOBS" ]; then
    echo "  $PASS SageMaker Training Jobs: None running"
else
    echo "  $FAIL SageMaker Training Jobs: $ACTIVE_JOBS still running! Stop immediately!"
    ISSUES=$((ISSUES+1))
fi

ACTIVE_ENDPOINTS=$(aws sagemaker list-endpoints \
    --region $REGION \
    --status-equals InService \
    --query 'length(Endpoints)' --output text 2>/dev/null)
if [ "$ACTIVE_ENDPOINTS" = "0" ] || [ -z "$ACTIVE_ENDPOINTS" ]; then
    echo "  $PASS SageMaker Endpoints: None running"
else
    echo "  $FAIL SageMaker Endpoints: $ACTIVE_ENDPOINTS still running! Very expensive!"
    ISSUES=$((ISSUES+1))
fi

# --- Summary ---
echo ""
echo "============================================================"
if [ "$ISSUES" = "0" ]; then
    echo "  $PASS ALL CLEAR! No billable resources detected."
    echo "  Your AWS costs have been stopped."
else
    echo "  $FAIL FOUND $ISSUES ISSUE(S). Review the items above."
    echo "  Run cleanup_aws.sh to destroy remaining resources."
fi
echo "============================================================"
echo ""
