#!/bin/bash
# downloads models from S3; charts are bundled in the deployment zip
set -euo pipefail

BUCKET="${S3_BUCKET:?S3_BUCKET environment variable is not set}"
MODELS=(random_forest svm neural_network gradient_boosting logistic_regression)

echo "downloading models from s3://$BUCKET"

mkdir -p data/processed/reports/figures models

aws s3 cp "s3://$BUCKET/processed/feature_columns.csv" data/processed/feature_columns.csv

for model in "${MODELS[@]}"; do
  mkdir -p "models/$model"
  aws s3 cp "s3://$BUCKET/models/$model/model.joblib" "models/$model/model.joblib"
  aws s3 cp "s3://$BUCKET/models/$model/metrics.json" "models/$model/metrics.json"
done

# optional: refresh charts from S3 if available
aws s3 cp "s3://$BUCKET/reports/model_comparison.csv" data/processed/reports/model_comparison.csv 2>/dev/null || true
aws s3 sync "s3://$BUCKET/reports/figures/" data/processed/reports/figures/ 2>/dev/null || true
aws s3 sync "s3://$BUCKET/reports/charts/" data/processed/reports/ --exclude "*" --include "*.png" 2>/dev/null || true

echo "S3 download complete"
