# plots for jupyter notebooks - shows charts inline instead of saving pngs

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from IPython.display import display
from sklearn.metrics import auc, classification_report, confusion_matrix, roc_curve


def show_metrics(metrics):
    display(pd.DataFrame([{
        "Accuracy": metrics["accuracy"],
        "Precision": metrics["precision"],
        "Recall": metrics["recall"],
        "F1": metrics["f1"],
        "Latency ms": metrics["latency_ms"],
    }]))


def show_classification_report(model, data):
    y_pred = model.predict(data["x_test"])
    print(classification_report(data["y_test"], y_pred, target_names=["Benign", "Attack"]))


def plot_confusion(model, data, title="confusion matrix"):
    y_pred = model.predict(data["x_test"])
    cm = confusion_matrix(data["y_test"], y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Benign", "Attack"], yticklabels=["Benign", "Attack"])
    plt.title(title)
    plt.tight_layout()
    plt.show()


def get_scores(model, x_test):
    if hasattr(model, "predict_proba"):
        return model.predict_proba(x_test)[:, 1]
    if hasattr(model, "decision_function"):
        return model.decision_function(x_test)
    return None


def plot_roc(model, data, title="ROC"):
    scores = get_scores(model, data["x_test"])
    if scores is None:
        print("cant do ROC for this one")
        return
    fpr, tpr, _ = roc_curve(data["y_test"], scores)
    plt.figure(figsize=(5, 4))
    plt.plot(fpr, tpr, label=f"auc={auc(fpr, tpr):.3f}")
    plt.plot([0, 1], [0, 1], "--", color="gray")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_feature_importance(model, data, title="top features", top_n=12):
    if not hasattr(model, "feature_importances_"):
        print("no importances for this model")
        return
    s = pd.Series(model.feature_importances_, index=data["features"])
    s = s.sort_values(ascending=False).head(top_n).sort_values()
    plt.figure(figsize=(8, 5))
    s.plot(kind="barh", color="green")
    plt.title(title)
    plt.tight_layout()
    plt.show()


def plot_errors_by_attack(model, data, title="mistakes by attack type"):
    y_pred = model.predict(data["x_test"])
    wrong = [data["attack_types"].iloc[i] for i in range(len(y_pred))
             if data["y_test"].iloc[i] != y_pred[i]]
    if not wrong:
        print("perfect on test set??")
        return
    counts = pd.Series(wrong).value_counts().head(10)
    plt.figure(figsize=(8, 4))
    counts.plot(kind="bar", color="coral")
    plt.title(title)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
