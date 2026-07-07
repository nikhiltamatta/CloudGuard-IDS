# looks at what attack types we keep getting wrong
# needed for the error analysis bit of the report

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import config
from attack_domains import get_group

MODELS = [
    "random_forest",
    "gradient_boosting",
    "neural_network",
    "svm",
    "logistic_regression",
]


def main():
    report_dir = config.DATA_DIR / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    all_errors = []

    for model_name in MODELS:
        err_path = config.MODELS_DIR / model_name / "errors.csv"
        if not err_path.exists():
            continue

        errors = pd.read_csv(err_path)
        errors["model"] = model_name
        errors["domain"] = errors["attack_type"].apply(get_group)
        all_errors.append(errors)

        summary = errors.groupby(["domain", "attack_type"]).size().reset_index(name="count")
        summary["model"] = model_name
        summary.to_csv(config.MODELS_DIR / model_name / "error_summary.csv", index=False)

    if not all_errors:
        print("no error files - train models first")
        return

    combined = pd.concat(all_errors, ignore_index=True)
    combined.to_csv(report_dir / "all_errors.csv", index=False)

    pivot = combined.groupby(["domain", "model"]).size().unstack(fill_value=0)
    pivot.to_csv(report_dir / "errors_by_domain.csv")

    plt.figure(figsize=(10, 5))
    sns.heatmap(pivot, annot=True, fmt="d", cmap="Reds")
    plt.title("misclassifications by attack type")
    plt.tight_layout()
    plt.savefig(report_dir / "error_heatmap.png")
    plt.close()

    # quick markdown summary we can copy from
    lines = ["# error analysis\n"]
    for model_name in MODELS:
        mpath = config.MODELS_DIR / model_name / "metrics.json"
        if mpath.exists():
            with open(mpath) as f:
                m = json.load(f)
            lines.append(f"- {model_name}: f1={m['f1']}, recall={m['recall']}, {m['latency_ms']}ms")

    lines.append("\n## worst mistakes\n")
    top = combined.groupby(["model", "attack_type"]).size().reset_index(name="count")
    top = top.sort_values("count", ascending=False).head(20)
    lines.append(top.to_string(index=False))

    with open(report_dir / "error_report.md", "w") as f:
        f.write("\n".join(lines))

    print(f"saved stuff to {report_dir}")


if __name__ == "__main__":
    main()
