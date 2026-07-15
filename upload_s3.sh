#!/bin/bash
# uploads processed data, models, and demo UI assets to s3
# make sure S3_BUCKET in config.py is set first

set -euo pipefail

BUCKET=$(python3 -c "import config; print(config.S3_BUCKET)")
echo "uploading to s3://$BUCKET"

# feature columns (needed for inference)
aws s3 sync data/processed/ s3://$BUCKET/processed/ \
  --exclude "reports/*" \
  --exclude "x_*.csv" \
  --exclude "y_*.csv" \
  --exclude "attack_type_*.csv" \
  --exclude "subsets/*"

# trained models + metrics
aws s3 sync models/ s3://$BUCKET/models/

# streamlit demo assets
if [ -f data/processed/reports/model_comparison.csv ]; then
  aws s3 cp data/processed/reports/model_comparison.csv s3://$BUCKET/reports/model_comparison.csv
fi

if [ -d data/processed/reports/figures ]; then
  aws s3 sync data/processed/reports/figures/ s3://$BUCKET/reports/figures/
fi

echo "done - verify with: aws s3 ls s3://$BUCKET/models/"
