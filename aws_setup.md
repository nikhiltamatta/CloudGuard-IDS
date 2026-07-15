# AWS deployment guide (AWS Academy Learner Lab)

Region: **us-west-2** (or us-east-1 — use the region your Learner Lab session is in)

Services used:
- **S3** — store models + demo assets
- **Elastic Beanstalk** — host the Flask inference UI (main deployment)
- **Lambda + API Gateway** — serverless inference API (comparison)

Live URLs:
- **Elastic Beanstalk UI:** http://cloudguard-ids-env.eba-4pjr7akk.us-west-2.elasticbeanstalk.com
- **Lambda API:** `POST https://x7crkb67sb.execute-api.us-west-2.amazonaws.com/prod/predict`

---

## 1. Start the lab and configure CLI

1. Open AWS Academy → start Learner Lab → copy CLI credentials.
2. Run:

```bash
aws configure
# region: us-east-1
```

If the lab gives a session token:

```bash
export AWS_SESSION_TOKEN="<your-session-token>"
```

Verify:

```bash
aws sts get-caller-identity
```

---

## 2. Create S3 bucket and upload artifacts

Pick a **globally unique** bucket name:

```bash
aws s3 mb s3://cloudguard-ids-yourname --region us-east-1
```

Set the same name in `config.py` (`S3_BUCKET`).

Upload models and UI files:

```bash
chmod +x upload_s3.sh build_deploy.sh
./upload_s3.sh
```

Verify:

```bash
aws s3 ls s3://cloudguard-ids-yourname/models/
aws s3 ls s3://cloudguard-ids-yourname/reports/figures/
```

---

## 3. Build Elastic Beanstalk zip

```bash
./build_deploy.sh
```

This creates `cloudguard-eb.zip` in the project root.

---

## 4. Deploy to Elastic Beanstalk (console)

1. AWS Console → **Elastic Beanstalk** → **Create application**
   - Name: `cloudguard-ids`
2. **Create environment** → Web server environment
   - Platform: **Python 3.11**
   - Upload `cloudguard-eb.zip`
3. **Configure more options**:
   - Service role: **LabRole**
   - EC2 instance profile: **LabInstanceProfile**
   - Instance type: **t3.small** (or t3.medium)
   - Capacity: **1** instance
   - Environment property: `S3_BUCKET` = your bucket name
4. Create environment and wait until health is **Ok**.

On startup the app downloads models from S3, then launches Streamlit on port 8000.

---

## 5. Test

Open the EB environment URL in a browser.

Check:
- model metrics load
- comparison tab shows table/charts
- classify button returns Benign/Attack

If it fails: EB console → **Logs** → **Request full logs** and look for S3 or startup errors.

---

## 6. Lambda + API Gateway

Deploy the serverless API:

```bash
chmod +x build_lambda.sh deploy_lambda.sh
./deploy_lambda.sh
```

This creates:
- Lambda function: `cloudguard-ids-predict`
- API Gateway: `POST /prod/predict`
- Default model in Lambda: `logistic_regression` (keeps package small)

Test:

```bash
curl -X POST "https://x7crkb67sb.execute-api.us-west-2.amazonaws.com/prod/predict" \
  -H "Content-Type: application/json" \
  -d '{"Destination Port": 80, "Flow Duration": 120, "Total Fwd Packets": 10}'
```

Example response:

```json
{"prediction": "Benign", "label_code": 0, "model": "logistic_regression", "latency_ms": 1.01}
```

Use this in the report to compare **serverless Lambda latency** vs **Elastic Beanstalk**.

---

## 7. Clean up (important — saves lab credits)

```bash
# terminate EB environment in the console first, then:
aws s3 rb s3://cloudguard-ids-yourname --force
```

Delete Lambda/API Gateway too if you created them.
