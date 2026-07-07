#!/bin/bash
# uploads processed data + models to s3
# make sure S3_BUCKET in config.py is set first

BUCKET=$(python3 -c "import config; print(config.S3_BUCKET)")
echo "uploading to s3://$BUCKET"
aws s3 sync data/processed/ s3://$BUCKET/processed/ --exclude "reports/*"
aws s3 sync models/ s3://$BUCKET/models/
echo "done"
