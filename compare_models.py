# pulls metrics from each model folder into one csv
# for the comparison table in the report

import json
import pandas as pd
import config

MODELS = [
    "random_forest",
    "gradient_boosting",
    "neural_network",
    "svm",
    "logistic_regression",
]


def main():
    rows = []
    for name in MODELS:
        path = config.MODELS_DIR / name / "metrics.json"
        if not path.exists():
            print(f"no metrics for {name} yet")
            continue
        with open(path) as f:
            m = json.load(f)
        rows.append({
            "model": name,
            "accuracy": m["accuracy"],
            "precision": m["precision"],
            "recall": m["recall"],
            "f1": m["f1"],
            "latency_ms": m["latency_ms"],
            "throughput": m["throughput"],
        })

    if not rows:
        print("nothing trained yet - run train_all.py")
        return

    df = pd.DataFrame(rows).sort_values("f1", ascending=False)
    out = config.DATA_DIR / "reports"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "model_comparison.csv", index=False)

    print(df.to_string(index=False))
    print(f"\nsaved {out / 'model_comparison.csv'}")


if __name__ == "__main__":
    main()
