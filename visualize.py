# makes png charts -> data/processed/reports/figures/
# stick these in the report

import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import auc, roc_curve

import config
import utils

MODELS = [
    "random_forest",
    "gradient_boosting",
    "neural_network",
    "svm",
    "logistic_regression",
]


def get_scores(model, x_test):
    if hasattr(model, "predict_proba"):
        return model.predict_proba(x_test)[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(x_test)
    return None


def plot_confusion(model_name, matrix, out_dir):
    plt.figure(figsize=(5, 4))
    sns.heatmap(
        np.array(matrix), annot=True, fmt="d", cmap="Blues",
        xticklabels=["Benign", "Attack"], yticklabels=["Benign", "Attack"],
    )
    plt.title(f"{model_name} confusion matrix")
    plt.ylabel("actual")
    plt.xlabel("predicted")
    plt.tight_layout()
    plt.savefig(out_dir / f"{model_name}_confusion.png", dpi=120)
    plt.close()


def plot_roc(model_name, y_true, scores, out_dir):
    fpr, tpr, _ = roc_curve(y_true, scores)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(5, 4))
    plt.plot(fpr, tpr, label=f"auc={roc_auc:.3f}")
    plt.plot([0, 1], [0, 1], "--", color="gray")
    plt.title(f"{model_name} ROC")
    plt.xlabel("fpr")
    plt.ylabel("tpr")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_dir / f"{model_name}_roc.png", dpi=120)
    plt.close()
    return fpr, tpr, roc_auc


def main():
    out_dir = config.DATA_DIR / "reports" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = utils.load_data()
    y_test = data["y_test"]
    comparison = []
    roc_lines = {}

    for model_name in MODELS:
        metrics_path = config.MODELS_DIR / model_name / "metrics.json"
        model_path = config.MODELS_DIR / model_name / "model.joblib"

        if not metrics_path.exists():
            print(f"skip {model_name} - not trained")
            continue

        with open(metrics_path) as f:
            metrics = json.load(f)

        plot_confusion(model_name, metrics["confusion_matrix"], out_dir)

        if model_path.exists():
            model = joblib.load(model_path)
            scores = get_scores(model, data["x_test"])
            if scores is not None:
                fpr, tpr, auc_val = plot_roc(model_name, y_test, scores, out_dir)
                roc_lines[model_name] = (fpr, tpr, auc_val)

        comparison.append({
            "model": model_name,
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "latency_ms": metrics["latency_ms"],
        })
        print(f"plots done for {model_name}")

    if not comparison:
        print("no models found")
        return

    df = pd.DataFrame(comparison)

    ax = df.set_index("model")[["accuracy", "precision", "recall", "f1"]].plot(kind="bar", figsize=(10, 5))
    ax.set_title("model comparison")
    ax.set_ylim(0, 1)
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(out_dir / "comparison_metrics.png", dpi=120)
    plt.close()

    plt.figure(figsize=(8, 4))
    df.plot(kind="bar", x="model", y="latency_ms", legend=False, color="coral")
    plt.title("latency (ms)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(out_dir / "comparison_latency.png", dpi=120)
    plt.close()

    if roc_lines:
        plt.figure(figsize=(6, 5))
        for name, (fpr, tpr, auc_val) in roc_lines.items():
            plt.plot(fpr, tpr, label=f"{name} ({auc_val:.3f})")
        plt.plot([0, 1], [0, 1], "--", color="gray")
        plt.title("ROC overlay")
        plt.legend(fontsize=8)
        plt.tight_layout()
        plt.savefig(out_dir / "comparison_roc.png", dpi=120)
        plt.close()

    print(f"figures in {out_dir}")


if __name__ == "__main__":
    main()
