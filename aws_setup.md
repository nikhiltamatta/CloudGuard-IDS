# AWS notes

We did this in AWS Academy Learner Lab. Might be slightly different if you're on a real account.

## What we actually used AWS for

- S3 to store processed data + trained models
- Lambda as a basic "classify this flow" API (prototype only, not production ready lol)

## Steps

### 1. CLI setup

```bash
aws configure
```

Copy the key + secret from the lab page. Region `us-east-1`.

### 2. Make a bucket

```bash
aws s3 mb s3://cloudguard-ids-yourname --region us-east-1
```

Change `S3_BUCKET` in `config.py` to match.

### 3. Upload

```bash
chmod +x upload_s3.sh
./upload_s3.sh
```

### 4. Lambda (if you have time)

Zip up:
- predict.py
- config.py
- models/random_forest/model.joblib  (or whatever model you want)
- data/processed/feature_columns.csv
- sklearn, pandas, numpy, joblib layers or bundle them

Handler: `predict.lambda_handler`

Hook up API gateway POST and test with something like:

```json
{"Destination Port": 80, "Flow Duration": 120, "Total Fwd Packets": 10}
```

### 5. Clean up after

Delete test resources when done or lab credits disappear fast.
