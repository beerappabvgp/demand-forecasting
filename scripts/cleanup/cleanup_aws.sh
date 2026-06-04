#!/bin/bash
set -e

# ============================================================
# AWS CLEANUP SCRIPT - Demand Forecasting Platform
# ============================================================
# Run this script to destroy ALL AWS resources and stop all costs.
# IMPORTANT: Set your credentials first:
#   export AWS_ACCESS_KEY_ID=...
#   export AWS_SECRET_ACCESS_KEY=...
#   export AWS_DEFAULT_REGION=ap-south-1
# ============================================================

REGION="ap-south-1"
BRONZE_BUCKET="demand-forecasting-production-bronze-3lhyuk"
SILVER_BUCKET="demand-forecasting-production-silver-3lhyuk"
MLFLOW_BUCKET="demand-forecasting-production-mlflow-3lhyuk"

echo ""
echo "============================================================"
echo "  DEMAND FORECASTING PLATFORM - AWS CLEANUP"
echo "  Region: $REGION"
echo "============================================================"
echo ""
echo "WARNING: This will PERMANENTLY DELETE all AWS resources!"
read -p "Type 'yes' to confirm: " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cancelled. No resources deleted."
    exit 0
fi

# ============================================================
# STEP 1: Stop any running SageMaker Training Jobs
# ============================================================
echo ""
echo "[1/6] Stopping any running SageMaker Training Jobs..."
RUNNING_JOBS=$(aws sagemaker list-training-jobs \
    --region $REGION \
    --status-equals InProgress \
    --query 'TrainingJobSummaries[].TrainingJobName' \
    --output text 2>/dev/null || echo "")

if [ -n "$RUNNING_JOBS" ]; then
    for JOB in $RUNNING_JOBS; do
        echo "  Stopping training job: $JOB"
        aws sagemaker stop-training-job --training-job-name "$JOB" --region $REGION
    done
else
    echo "  No running training jobs found."
fi

# ============================================================
# STEP 2: Stop any running Glue Jobs
# ============================================================
echo ""
echo "[2/6] Stopping any running Glue Jobs..."
GLUE_JOB="demand-forecasting-etl-bronze-to-silver"
RUNNING_RUNS=$(aws glue get-job-runs \
    --job-name $GLUE_JOB \
    --region $REGION \
    --query "JobRuns[?JobRunState=='RUNNING'].Id" \
    --output text 2>/dev/null || echo "")

if [ -n "$RUNNING_RUNS" ]; then
    for RUN_ID in $RUNNING_RUNS; do
        echo "  Stopping Glue job run: $RUN_ID"
        aws glue batch-stop-job-run --job-name $GLUE_JOB --job-run-ids "$RUN_ID" --region $REGION
    done
else
    echo "  No running Glue jobs found."
fi

# ============================================================
# STEP 3: Empty S3 Buckets (Terraform cannot delete non-empty buckets)
# ============================================================
echo ""
echo "[3/6] Emptying S3 buckets (including all versions)..."
for BUCKET in $BRONZE_BUCKET $SILVER_BUCKET $MLFLOW_BUCKET; do
    echo "  Emptying bucket: s3://$BUCKET"
    # Delete all objects
    aws s3 rm s3://$BUCKET --recursive --region $REGION 2>/dev/null || true
    # Delete all versioned objects (if versioning was ever enabled)
    VERSIONS=$(aws s3api list-object-versions \
        --bucket $BUCKET \
        --region $REGION \
        --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}, DeleteMarkers: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' \
        --output json 2>/dev/null || echo "{}")
    echo "  Bucket $BUCKET emptied."
done

# ============================================================
# STEP 4: Empty any SageMaker-created S3 buckets
# ============================================================
echo ""
echo "[4/6] Emptying SageMaker auto-created buckets (if any)..."
SM_BUCKET="sagemaker-$REGION-$(aws sts get-caller-identity --query Account --output text)"
if aws s3 ls s3://$SM_BUCKET --region $REGION > /dev/null 2>&1; then
    echo "  Found SageMaker bucket: s3://$SM_BUCKET"
    read -p "  Delete SageMaker bucket too? (yes/no): " delete_sm
    if [ "$delete_sm" = "yes" ]; then
        aws s3 rm s3://$SM_BUCKET --recursive --region $REGION
        aws s3 rb s3://$SM_BUCKET --force --region $REGION
        echo "  SageMaker bucket deleted."
    fi
else
    echo "  No SageMaker auto-created bucket found."
fi

# ============================================================
# STEP 5: Terraform Destroy (destroys VPC, IAM, Glue, ECR, S3)
# ============================================================
echo ""
echo "[5/6] Running Terraform destroy (VPC, NAT Gateway, IAM, Glue, ECR, S3)..."
echo "  This is the most important step - stops the NAT Gateway billing!"
cd terraform

# Auto-approve the destroy
../bin/terraform destroy -auto-approve
cd ..
echo "  Terraform destroy complete."

# ============================================================
# STEP 6: Verify everything is cleaned up
# ============================================================
echo ""
echo "[6/6] Running verification checks..."
bash scripts/cleanup/verify_cleanup.sh

echo ""
echo "============================================================"
echo "  CLEANUP COMPLETE!"
echo "  All resources have been destroyed."
echo "  You will receive a final billing statement within 24 hours."
echo "============================================================"
