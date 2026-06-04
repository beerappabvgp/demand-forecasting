#!/bin/bash
set -e

# ============================================================
# BUILD & PUSH DOCKER IMAGE TO ECR
# ============================================================
# This script builds the FastAPI serving container and pushes
# it to the AWS ECR repository created by Terraform.
#
# Run from the project root:
#   bash scripts/docker/build_and_push_ecr.sh
# ============================================================

REGION="ap-south-1"
ACCOUNT_ID="473469900710"
ECR_REPO="demand-forecasting-serving"
IMAGE_TAG="latest"
ECR_URL="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${ECR_REPO}"

echo ""
echo "============================================================"
echo "  BUILD & PUSH TO ECR"
echo "  Target: ${ECR_URL}:${IMAGE_TAG}"
echo "============================================================"

# Step 1: Authenticate Docker with ECR
echo ""
echo "[1/4] Authenticating Docker with ECR..."
aws ecr get-login-password --region $REGION | \
    docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
echo "  Authentication successful."

# Step 2: Build the Docker image
echo ""
echo "[2/4] Building Docker image..."
echo "  This may take 3-5 minutes on first build (downloading base Python image)..."
docker build \
    --platform linux/amd64 \
    -t "${ECR_REPO}:${IMAGE_TAG}" \
    -f Dockerfile \
    .
echo "  Build complete."

# Step 3: Tag the image for ECR
echo ""
echo "[3/4] Tagging image for ECR..."
docker tag "${ECR_REPO}:${IMAGE_TAG}" "${ECR_URL}:${IMAGE_TAG}"
echo "  Tagged: ${ECR_URL}:${IMAGE_TAG}"

# Step 4: Push to ECR
echo ""
echo "[4/4] Pushing image to ECR..."
echo "  Uploading layers... (may take 2-5 minutes)"
docker push "${ECR_URL}:${IMAGE_TAG}"

echo ""
echo "============================================================"
echo "  PUSH COMPLETE!"
echo "  Image: ${ECR_URL}:${IMAGE_TAG}"
echo ""
echo "  To verify the push:"
echo "  aws ecr describe-images --repository-name ${ECR_REPO} --region ${REGION} --output table"
echo "============================================================"
