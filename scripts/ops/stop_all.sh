#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# scripts/ops/stop_all.sh
# Manually stops ALL resources immediately (ECS + NAT GW).
# Use this any time you want to save costs right now.
# ─────────────────────────────────────────────────────────────────
set -e

LAMBDA_NAME="demand-forecasting-resource-scheduler"
AWS_REGION="ap-south-1"

echo "🔴 Invoking scheduler Lambda with action=stop ..."
aws lambda invoke \
  --function-name "$LAMBDA_NAME" \
  --region "$AWS_REGION" \
  --payload '{"action": "stop"}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/lambda_response.json

echo ""
echo "📋 Lambda response:"
cat /tmp/lambda_response.json
echo ""
echo ""
echo "✅ All resources are being stopped:"
echo "   - ECS service: desired_count set to 0"
echo "   - NAT Gateway: deletion initiated (takes ~30 seconds)"
echo ""
echo "💰 Cost savings are now active!"
