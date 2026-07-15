# AWS deployment guide (AWS Academy Learner Lab)

Region: **us-west-2** (match whatever region your Learner Lab session gives you)

Services used:
- **S3** — models, report charts, deploy zips
- **Elastic Beanstalk** — Flask demo UI (main deployment; same app as local)
- **Lambda + API Gateway** — serverless `/predict` API (RQ2 comparison)

### Live URLs (current lab account)

| Service | URL |
|---------|-----|
| **Elastic Beanstalk UI** | http://cloudguard-ids-env.eba-4pjr7akk.us-west-2.elasticbeanstalk.com |
| **Learning curves tab** | http://cloudguard-ids-env.eba-4pjr7akk.us-west-2.elasticbeanstalk.com/?tab=curves |
| **Compare tab** | http://cloudguard-ids-env.eba-4pjr7akk.us-west-2.elasticbeanstalk.com/?tab=compare |
| **Lambda API (GET = health)** | https://x7crkb67sb.execute-api.us-west-2.amazonaws.com/prod/predict |
| **Lambda API (POST = predict)** | same URL — must send JSON body |

S3 bucket: `cloudguard-ids-nikhil-341757264632`

Local demo uses the **same Flask app** (`application.py` / `python3 run_demo.py` → http://localhost:8000).

---

## 1. Start the lab and configure CLI

1. Open AWS Academy → start Learner Lab → copy CLI credentials.
2. Export them (Learner Lab creds expire; refresh when you get `voc-cancel-cred` errors):

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_SESSION_TOKEN="..."
export AWS_DEFAULT_REGION=us-west-2
```

Or run `aws configure` then export the session token.

Verify:

```bash
aws sts get-caller-identity
```

---

## 2. Create S3 bucket and upload artifacts

Bucket name must be **globally unique**:

```bash
aws s3 mb s3://cloudguard-ids-nikhil-341757264632 --region us-west-2
```

Set the same name in `config.py` (`S3_BUCKET`), or rely on the default / EB env var.

Upload models + charts:

```bash
chmod +x upload_s3.sh build_deploy.sh deploy_lambda.sh
./upload_s3.sh
```

This syncs:
- `models/` → `s3://…/models/`
- figure PNGs → `s3://…/reports/figures/`
- learning curves + error heatmap → `s3://…/reports/charts/`
- `model_comparison.csv` → `s3://…/reports/`

Verify:

```bash
aws s3 ls s3://cloudguard-ids-nikhil-341757264632/models/
aws s3 ls s3://cloudguard-ids-nikhil-341757264632/reports/figures/
aws s3 ls s3://cloudguard-ids-nikhil-341757264632/reports/charts/
```

---

## 3. Build Elastic Beanstalk zip

```bash
./build_deploy.sh
```

Creates `cloudguard-eb.zip` with:
- Flask app (`application.py` — same as local)
- `config.py`, `predict.py`, Procfile, startup
- **bundled charts** (figures, learning curves, error heatmap, comparison CSV)

Charts are inside the zip so the UI still shows graphs even if S3 chart download fails.

---

## 4. Deploy to Elastic Beanstalk

### CLI (what we used)

```bash
BUCKET=cloudguard-ids-nikhil-341757264632
aws s3 cp cloudguard-eb.zip s3://$BUCKET/deploy/cloudguard-eb-v5.zip
aws elasticbeanstalk create-application-version \
  --application-name cloudguard-ids \
  --version-label v5 \
  --source-bundle S3Bucket=$BUCKET,S3Key=deploy/cloudguard-eb-v5.zip \
  --process
aws elasticbeanstalk update-environment \
  --environment-name cloudguard-ids-env \
  --version-label v5
```

### Console (first-time create)

1. AWS Console → **Elastic Beanstalk** → **Create application** `cloudguard-ids`
2. **Create environment** → Web server → Platform **Python 3.11** → upload zip
3. **Configure more options**:
   - Service role: **LabRole**
   - EC2 instance profile: **LabInstanceProfile**
   - Instance type: **t3.small** (or t3.medium)
   - Capacity: **1** instance
   - Environment property: `S3_BUCKET` = your bucket name
4. Wait until health is **Ok / Green**.

On startup (`startup.sh`) the app downloads **models** from S3, then **gunicorn** serves Flask on port 8000. Charts ship inside the zip.

---

## 5. Test the Flask UI

Open the EB URL. Tabs:

| Tab | What to check |
|-----|----------------|
| **my model** | metrics + confusion / ROC / PR / feature plots |
| **compare everyone** | comparison table + metric/latency/ROC charts + error heatmap |
| **learning curves** | all 5 model learning-curve PNGs |
| **try a prediction** | classify returns Benign/Attack + latency |

Direct image check example:
`/reports/learning_curve_random_forest.png` should return HTTP 200.

If it fails: EB → **Logs** → **Request full logs** (look for S3 / gunicorn / sklearn errors).

---

## 6. Lambda + API Gateway

```bash
./deploy_lambda.sh
```

Creates / updates:
- Lambda: `cloudguard-ids-predict` (default model: `logistic_regression` — keeps package under size limits)
- API Gateway: `cloudguard-ids-api`
  - **GET** `/prod/predict` — health + usage JSON (works in a browser)
  - **POST** `/prod/predict` — real prediction

Opening the URL in a browser uses GET (that is expected). Prediction needs POST.

```bash
# health (also works if you paste the URL in Chrome)
curl "https://x7crkb67sb.execute-api.us-west-2.amazonaws.com/prod/predict"

# prediction
curl -X POST "https://x7crkb67sb.execute-api.us-west-2.amazonaws.com/prod/predict" \
  -H "Content-Type: application/json" \
  -d '{"Destination Port": 80, "Flow Duration": 120, "Total Fwd Packets": 10}'
```

Example POST response:

```json
{"prediction": "Benign", "label_code": 0, "model": "logistic_regression", "latency_ms": 1.01}
```

Use this in the report to compare **serverless Lambda latency** vs **Elastic Beanstalk Flask**.

---

## 7. Local vs cloud (same UI)

| | Local | Elastic Beanstalk |
|--|-------|-------------------|
| App | `python3 run_demo.py` | gunicorn + `application.py` |
| URL | http://localhost:8000 | EB CNAME above |
| Framework | Flask | Flask |

Do **not** use the old Streamlit app (`ui/app.py`) — it is deprecated.

---

## 8. Clean up (saves lab credits)

```bash
# terminate EB environment in the console first, then:
aws s3 rb s3://cloudguard-ids-nikhil-341757264632 --force
aws lambda delete-function --function-name cloudguard-ids-predict
# delete API Gateway cloudguard-ids-api in the console if needed
```
