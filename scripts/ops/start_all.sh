#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# scripts/ops/start_all.sh
# Manually starts ALL resources immediately (NAT GW + ECS).
# Use this any time you want to work outside the 9AM-6PM IST schedule.
# ─────────────────────────────────────────────────────────────────
set -e

LAMBDA_NAME="demand-forecasting-resource-scheduler"
AWS_REGION="ap-south-1"

echo "🟢 Invoking scheduler Lambda with action=start ..."
aws lambda invoke \
  --function-name "$LAMBDA_NAME" \
  --region "$AWS_REGION" \
  --payload '{"action": "start"}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/lambda_response.json

echo ""
echo "📋 Lambda response:"
cat /tmp/lambda_response.json
echo ""
echo ""
echo "⏳ NAT Gateway takes ~90 seconds to become available."
echo "   ECS service will start pulling the container image after NAT GW is ready."
echo ""
echo "✅ To check when the API is live, run:"
echo "   curl http://demand-forecasting-alb-494652046.ap-south-1.elb.amazonaws.com/health"
