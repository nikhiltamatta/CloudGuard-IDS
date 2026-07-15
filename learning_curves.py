# learning curves - lecturer wants to see performance vs training set size
# warning: retrains everything 4 times, go do something else

import matplotlib.pyplot as plt
import pandas as pd

import config
import train_random_forest
import train_svm
import train_neural_network
import train_gradient_boosting
import train_logistic_regression

TRAINERS = {
    "random_forest": train_random_forest,
    "svm": train_svm,
    "neural_network": train_neural_network,
    "gradient_boosting": train_gradient_boosting,
    "logistic_regression": train_logistic_regression,
}


def y_limits(scores):
    """zoom y-axis when scores cluster near 1.0 so curves are readable"""
    low = min(scores)
    high = max(scores)
    spread = high - low

    if low >= 0.9:
        pad = max(0.001, spread * 0.25, 0.003)
        return max(0.0, low - pad), min(1.0, high + pad)
    if low >= 0.5:
        pad = max(0.03, spread * 0.15)
        return max(0.0, low - pad), min(1.0, high + pad)
    return 0, 1


def plot_curves(df, report_dir):
    for model_name in TRAINERS:
        sub = df[df["model"] == model_name]
        scores = sub["f1"].tolist() + sub["recall"].tolist()
        ymin, ymax = y_limits(scores)

        plt.figure(figsize=(6, 4))
        plt.plot(sub["data_fraction"], sub["f1"], "o-", label="F1")
        plt.plot(sub["data_fraction"], sub["recall"], "s-", label="Recall")
        plt.title(f"learning curve - {model_name}")
        plt.xlabel("fraction of training data")
        plt.ylabel("score")
        plt.ylim(ymin, ymax)
        plt.legend()
        plt.tight_layout()
        plt.savefig(report_dir / f"learning_curve_{model_name}.png", dpi=120)
        plt.close()


def main():
    print("learning curves starting...")
    print("(yeah this takes forever)\n")

    results = []
    report_dir = config.DATA_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    for model_name, trainer in TRAINERS.items():
        for pct in config.SUBSET_SIZES:
            subset = f"train_{int(pct * 100)}pct"
            print(f"  {model_name} on {subset}")

            save_path = config.MODELS_DIR / model_name / "learning_curve" / subset
            metrics = trainer.train(subset=subset, save_to=save_path)
            results.append({
                "model": model_name,
                "subset": subset,
                "data_fraction": pct,
                "f1": metrics["f1"],
                "recall": metrics["recall"],
                "latency_ms": metrics["latency_ms"],
            })

    df = pd.DataFrame(results)
    df.to_csv(report_dir / "learning_curves.csv", index=False)
    plot_curves(df, report_dir)

    print(f"done, check {report_dir}")


if __name__ == "__main__":
    import sys

    report_dir = config.DATA_DIR / "reports"
    csv_path = report_dir / "learning_curves.csv"

    if len(sys.argv) > 1 and sys.argv[1] == "--plots-only":
        if not csv_path.exists():
            print(f"missing {csv_path} - run full learning_curves.py first")
            raise SystemExit(1)
        df = pd.read_csv(csv_path)
        plot_curves(df, report_dir)
        print(f"replotted learning curves in {report_dir}")
    else:
        main()
