#!/bin/bash
# deploys Lambda + API Gateway for CloudGuard-IDS
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
REGION="${AWS_DEFAULT_REGION:-us-west-2}"
ACCOUNT="${AWS_ACCOUNT_ID:-341757264632}"
FUNCTION="cloudguard-ids-predict"
ROLE_ARN="arn:aws:iam::${ACCOUNT}:role/LabRole"
BUCKET="cloudguard-ids-nikhil-341757264632"
ZIP="$ROOT/lambda/lambda.zip"

"$ROOT/build_lambda.sh"

if [ ! -f "$ZIP" ]; then
  echo "lambda.zip not found"
  exit 1
fi

ZIP_SIZE=$(stat -f%z "$ZIP" 2>/dev/null || stat -c%s "$ZIP")
S3_KEY="deploy/lambda.zip"

if [ "$ZIP_SIZE" -gt 50000000 ]; then
  echo "uploading large zip to s3://$BUCKET/$S3_KEY"
  aws s3 cp "$ZIP" "s3://$BUCKET/$S3_KEY"
  CODE_ARG="S3Bucket=$BUCKET,S3Key=$S3_KEY"
else
  CODE_ARG="ZipFile=fileb://$ZIP"
fi

if aws lambda get-function --function-name "$FUNCTION" >/dev/null 2>&1; then
  echo "updating Lambda function $FUNCTION"
  if [ "$ZIP_SIZE" -gt 50000000 ]; then
    aws lambda update-function-code --function-name "$FUNCTION" --s3-bucket "$BUCKET" --s3-key "$S3_KEY"
  else
    aws lambda update-function-code --function-name "$FUNCTION" --zip-file "fileb://$ZIP"
  fi
  aws lambda update-function-configuration \
    --function-name "$FUNCTION" \
    --runtime python3.11 \
    --handler predict.lambda_handler \
    --role "$ROLE_ARN" \
    --timeout 30 \
    --memory-size 1024
else
  echo "creating Lambda function $FUNCTION"
  if [ "$ZIP_SIZE" -gt 50000000 ]; then
    aws lambda create-function \
      --function-name "$FUNCTION" \
      --runtime python3.11 \
      --role "$ROLE_ARN" \
      --handler predict.lambda_handler \
      --code "S3Bucket=$BUCKET,S3Key=$S3_KEY" \
      --timeout 30 \
      --memory-size 1024
  else
    aws lambda create-function \
      --function-name "$FUNCTION" \
      --runtime python3.11 \
      --role "$ROLE_ARN" \
      --handler predict.lambda_handler \
      --zip-file "fileb://$ZIP" \
      --timeout 30 \
      --memory-size 1024
  fi
fi

FUNCTION_ARN=$(aws lambda get-function --function-name "$FUNCTION" --query 'Configuration.FunctionArn' --output text)
echo "Lambda ARN: $FUNCTION_ARN"

API_NAME="cloudguard-ids-api"
API_ID=$(aws apigateway get-rest-apis --query "items[?name=='$API_NAME'].id" --output text)

if [ -z "$API_ID" ] || [ "$API_ID" = "None" ]; then
  API_ID=$(aws apigateway create-rest-api --name "$API_NAME" --description "CloudGuard-IDS inference API" --endpoint-configuration types=REGIONAL --query id --output text)
  echo "created API Gateway: $API_ID"
else
  echo "using existing API Gateway: $API_ID"
fi

ROOT_ID=$(aws apigateway get-resources --rest-api-id "$API_ID" --query "items[?path=='/'].id" --output text)
RESOURCE_ID=$(aws apigateway get-resources --rest-api-id "$API_ID" --query "items[?path=='/predict'].id" --output text)

if [ -z "$RESOURCE_ID" ] || [ "$RESOURCE_ID" = "None" ]; then
  RESOURCE_ID=$(aws apigateway create-resource --rest-api-id "$API_ID" --parent-id "$ROOT_ID" --path-part predict --query id --output text)
fi

aws apigateway put-method \
  --rest-api-id "$API_ID" \
  --resource-id "$RESOURCE_ID" \
  --http-method POST \
  --authorization-type NONE >/dev/null 2>&1 || true

aws apigateway put-integration \
  --rest-api-id "$API_ID" \
  --resource-id "$RESOURCE_ID" \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${FUNCTION_ARN}/invocations"

aws lambda add-permission \
  --function-name "$FUNCTION" \
  --statement-id "apigateway-${API_ID}" \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT}:${API_ID}/*/*" \
  >/dev/null 2>&1 || true

aws apigateway create-deployment --rest-api-id "$API_ID" --stage-name prod >/dev/null

API_URL="https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/predict"
echo ""
echo "Lambda + API Gateway deployed"
echo "POST $API_URL"
echo 'Body: {"Destination Port": 80, "Flow Duration": 120, "Total Fwd Packets": 10}'
