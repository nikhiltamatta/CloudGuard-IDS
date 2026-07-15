# How to run everything

Quick guide we wrote for ourselves so we dont forget the order.

---

## 1. Setup (once)

```bash
cd CloudGuard-IDS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Needs **Flask** (local demo + same code as AWS). If pip complains, upgrade it or use `pip3`. Works on Mac; Windows should be similar.

---

## 2. Dataset

All 8 csv files need to be in `dataset/`. Check:

```bash
ls dataset/
```

If you get "cant find file" during preprocess thats usually why. Details in `dataset/README.md`.

---

## 3. Preprocess

```bash
python3 preprocess.py
python3 make_subsets.py
```

`preprocess.py` took like 15-20 mins on Nikhil's mac. Go get food.

Outputs go to `data/processed/`.

---

## 4. Train

Everything:
```bash
python3 train_all.py
```

Just your own model (for the demo video):
```bash
python3 train_random_forest.py      # Nikhil
python3 train_svm.py                # Ishan  <- slowest one btw
python3 train_neural_network.py     # Aman
python3 train_gradient_boosting.py  # Ajay
python3 train_logistic_regression.py
```

Models land in `models/<name>/` (`model.joblib` + `metrics.json`).

---

## 5. Results + graphs

```bash
python3 compare_models.py
python3 visualize.py
python3 error_analysis.py
```

Outputs:
- `data/processed/reports/model_comparison.csv`
- `data/processed/reports/figures/*.png` (confusion, ROC, PR, feature importance, comparison charts)
- `data/processed/reports/error_heatmap.png`

Learning curves (lecturer wants this in the report):
```bash
python3 learning_curves.py
```

Fair warning — learning curves retrains every model several times. Ishan's SVM on full data already took ages so we only used 25% for that one.

If you already have `learning_curves.csv` and only need to replot (zoomed axes):
```bash
python3 learning_curves.py --plots-only
```

PNGs: `data/processed/reports/learning_curve_*.png`

---

## 6. Demo (Flask — same as Elastic Beanstalk)

```bash
python3 run_demo.py
```

Opens **http://localhost:8000**

Tabs in the UI:
- **my model** — pick a model, see metrics + plots
- **compare everyone** — table + comparison charts + error heatmap
- **learning curves** — zoomed F1 vs training-size plots
- **try a prediction** — classify a sample flow

You can also run:
```bash
python3 application.py
```

`ui/app.py` is the **old Streamlit** UI — ignore it / deprecated.

**Jupyter (what we'd use for the video):**
```bash
jupyter notebook notebooks/
```
Open your notebook → Cell → Run All. Shows the numbers and charts.

---

## 7. AWS

Full steps: `aws_setup.md`.

Short version:
```bash
./upload_s3.sh          # models + charts to S3
./build_deploy.sh       # cloudguard-eb.zip (Flask + bundled charts)
./deploy_lambda.sh      # Lambda + API Gateway
```

Live EB demo (when lab is running):
http://cloudguard-ids-env.eba-4pjr7akk.us-west-2.elasticbeanstalk.com

Lambda:
- GET  https://x7crkb67sb.execute-api.us-west-2.amazonaws.com/prod/predict  (health)
- POST same URL with JSON body (prediction)

---

## Before we submit

- [ ] csvs in dataset/
- [ ] preprocess ran ok
- [ ] all 4 models trained (+ baseline)
- [ ] compare_models.py done
- [ ] visualize.py done (pngs in data/processed/reports/figures)
- [ ] error analysis done
- [ ] learning curves done (`learning_curve_*.png`)
- [ ] Flask demo works locally (`run_demo.py` → localhost:8000)
- [ ] AWS EB UI up (charts + curves tabs)
- [ ] Lambda POST predict works
- [ ] demo video recorded
- [ ] ML strategy page filled in
- [ ] report done
- [ ] everyone shows up for presentation
