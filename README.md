# CloudGuard-IDS

Our H9CML group project — trying to detect network attacks with ML and stick it on AWS.

Dataset: **CICIDS 2017** (the 8 csv files everyone uses for IDS coursework)

### Research questions

**RQ1:** Can ML actually tell benign traffic apart from attacks on CICIDS 2017?

**RQ2:** Which model is the best pick for AWS if we care about both F1 score and how fast it runs?

We said "best" = highest F1, and if two models are basically the same we go with the faster one. More write-up stuff is in `REPORT_INTRODUCTION.md` if you're doing the report.

---

## Who did what

| Person | Model | File to run |
|--------|-------|-------------|
| Nikhil | Random Forest | `train_random_forest.py` |
| Ishan | SVM | `train_svm.py` |
| Aman | Neural Network | `train_neural_network.py` |
| Ajay | Gradient Boosting | `train_gradient_boosting.py` |
| all of us | Logistic Regression (baseline) | `train_logistic_regression.py` |

---

## Getting it running

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 preprocess.py        # do this first, takes a while
python3 make_subsets.py
python3 train_all.py         # or just your own train script
python3 compare_models.py
python3 visualize.py
```

Full steps in `HOW_TO_RUN.md` — read that if something breaks.

---

## What's in the folder

```
config.py           settings / paths
preprocess.py       cleans the raw csvs
make_subsets.py     smaller train sets for learning curves
utils.py            stuff we all share (load data, metrics etc)
train_*.py          one per person
compare_models.py   puts everyones results in one table
learning_curves.py  retrains on 10/25/50/100% data (slow!)
error_analysis.py   which attacks did we mess up
visualize.py        saves png charts for report
predict.py          single prediction + lambda
run_demo.py         opens streamlit app
dataset/            put raw csvs here
data/processed/     output from preprocess (auto generated)
models/             saved models go here
notebooks/          jupyter notebooks for demo video
ui/app.py           streamlit
```

---

## Dataset

Grab CICIDS 2017 online and drop the 8 csv files into `dataset/`. We already have them in there but your laptop might not.

---

## Demo / video

Streamlit:
```bash
python3 run_demo.py
```

Jupyter (probably easier for the 4 min video):
```bash
jupyter notebook notebooks/random_forest.ipynb   # change to your notebook
```

Notebooks we made:
- `notebooks/random_forest.ipynb` — Nikhil
- `notebooks/svm.ipynb` — Ishan
- `notebooks/neural_network.ipynb` — Aman
- `notebooks/gradient_boosting.ipynb` — Ajay
- `notebooks/logistic_regression.ipynb` — baseline
- `notebooks/team_run_all.ipynb` — compare everyone

---

## AWS bit

We upload to S3, deploy the demo on **Elastic Beanstalk** (Flask UI), and expose a **Lambda + API Gateway** endpoint for serverless comparison. See `aws_setup.md`.

Quick deploy:

```bash
# S3 artifacts
./upload_s3.sh

# Elastic Beanstalk UI
./build_deploy.sh

# Lambda API (optional comparison)
./deploy_lambda.sh
```

---

## Stuff to hand in (from the brief)

- IEEE report (team, 5-6 pages)
- code + dataset zip (each person)
- 4 min demo video (each person)
- 1 page ML strategy (each person) — template in `ML_STRATEGY_TEMPLATE.md`
- 9 min presentation (everyone has to show up or you get 0)
