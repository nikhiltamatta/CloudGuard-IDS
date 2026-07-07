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

If pip complains just upgrade it or use `pip3`. Works on Mac, should work on Windows with minor changes.

---

## 2. Dataset

All 8 csv files need to be in `dataset/`. Check:

```bash
ls dataset/
```

If you get "cant find file" during preprocess thats usually why.

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

---

## 5. Results + graphs

```bash
python3 compare_models.py
python3 visualize.py
python3 error_analysis.py
```

Learning curves (lecturer wants this in the report):
```bash
python3 learning_curves.py
```

Fair warning — learning curves retrains every model 4 times. Ishan's SVM on full data already took ages so we only used 25% for that one.

---

## 6. Demo

**Streamlit:**
```bash
python3 run_demo.py
```
Opens http://localhost:8501

**Jupyter (what we'd use for the video):**
```bash
jupyter notebook notebooks/
```
Open your notebook → Cell → Run All. Shows the numbers and charts.

---

## 7. AWS

Optional but we need it for the cloud part of the marks. See `aws_setup.md`.

---

## Before we submit

- [ ] csvs in dataset/
- [ ] preprocess ran ok
- [ ] all 4 models trained (+ baseline)
- [ ] compare_models.py done
- [ ] visualize.py done (pngs in data/processed/reports/figures)
- [ ] error analysis done
- [ ] learning curves done (or at least started...)
- [ ] demo video recorded
- [ ] ML strategy page filled in
- [ ] report done
- [ ] everyone shows up for presentation
