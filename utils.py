# shared code - Nikhil and Ishan wrote most of this so we didnt repeat ourselves in every train script
# if something breaks here it breaks everywhere lol

import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

import config


def load_data(subset=None):
    """loads csvs from data/processed. subset='train_25pct' for learning curves."""
    data_dir = config.DATA_DIR

    if subset:
        folder = data_dir / "subsets"
        x_train = pd.read_csv(folder / f"{subset}_x.csv")
        y_train = pd.read_csv(folder / f"{subset}_y.csv")["label"]
    else:
        x_train = pd.read_csv(data_dir / "x_train.csv")
        y_train = pd.read_csv(data_dir / "y_train.csv")["label"]

    return {
        "x_train": x_train,
        "y_train": y_train,
        "x_val": pd.read_csv(data_dir / "x_val.csv"),
        "y_val": pd.read_csv(data_dir / "y_val.csv")["label"],
        "x_test": pd.read_csv(data_dir / "x_test.csv"),
        "y_test": pd.read_csv(data_dir / "y_test.csv")["label"],
        "attack_types": pd.read_csv(data_dir / "attack_type_test.csv")["attack_type"],
        "features": pd.read_csv(data_dir / "feature_columns.csv")["feature"].tolist(),
    }


def check_latency(model, x_test, runs=5):
    # rough timing - predict on max 1000 rows, average a few runs
    sample = x_test.head(min(1000, len(x_test)))
    times = []
    for _ in range(runs):
        t0 = time.time()
        model.predict(sample)
        times.append((time.time() - t0) * 1000)
    return round(float(np.mean(times)), 2)


def get_metrics(model, data, model_name):
    y_pred = model.predict(data["x_test"])
    y_true = data["y_test"]
    latency = check_latency(model, data["x_test"])

    return {
        "model": model_name,
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "latency_ms": latency,
        "throughput": round(1000 / latency, 2) if latency > 0 else 0,
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "test_rows": len(y_true),
    }


def save_model(model, metrics, model_name, out_dir=None):
    out = out_dir or (config.MODELS_DIR / model_name)
    out.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, out / "model.joblib")
    with open(out / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # print so you can see results in terminal
    print(f"\n--- {model_name} ---")
    print(f"acc={metrics['accuracy']}  f1={metrics['f1']}  recall={metrics['recall']}")
    print(f"latency={metrics['latency_ms']}ms  saved to {out}\n")


def save_errors(model, data, model_name, out_dir=None):
    # wrong predictions -> csv for error analysis section of report
    y_pred = model.predict(data["x_test"])
    y_true = data["y_test"]
    attacks = data["attack_types"]

    wrong = []
    for i in range(len(y_true)):
        if y_true.iloc[i] != y_pred[i]:
            wrong.append({
                "row": i,
                "actual": int(y_true.iloc[i]),
                "predicted": int(y_pred[i]),
                "attack_type": attacks.iloc[i],
            })

    folder = out_dir or (config.MODELS_DIR / model_name)
    folder.mkdir(parents=True, exist_ok=True)
    out = folder / "errors.csv"
    pd.DataFrame(wrong).to_csv(out, index=False)
    print(f"{len(wrong)} wrong predictions -> {out}")
