#!/usr/bin/env python3
# generates jupyter notebooks - only rerun if you change notebook layout

import json
from pathlib import Path

NOTEBOOKS = [
    {
        "file": "random_forest.ipynb",
        "title": "Random Forest - Nikhil",
        "member": "Nikhil",
        "model": "Random Forest",
        "import_train": "train_random_forest",
        "subset_note": "full train data",
        "extra_importance": True,
        "train_warning": "might take a few mins",
    },
    {
        "file": "svm.ipynb",
        "title": "SVM - Ishan",
        "member": "Ishan",
        "model": "Support Vector Machine (LinearSVC)",
        "import_train": "train_svm",
        "subset_note": "only 25% train data cause full svm took forever on my laptop",
        "extra_importance": False,
        "train_warning": "yeah svm is slow, sorry",
    },
    {
        "file": "neural_network.ipynb",
        "title": "Neural Network - Aman",
        "member": "Aman",
        "model": "MLP Neural Network",
        "import_train": "train_neural_network",
        "subset_note": "full train data",
        "extra_importance": False,
        "train_warning": "neural net takes a while too, ~5-10 min maybe",
    },
    {
        "file": "gradient_boosting.ipynb",
        "title": "Gradient Boosting - Ajay",
        "member": "Ajay",
        "model": "Gradient Boosting",
        "import_train": "train_gradient_boosting",
        "subset_note": "full train data",
        "extra_importance": True,
        "train_warning": "",
    },
    {
        "file": "logistic_regression.ipynb",
        "title": "Logistic Regression - Baseline",
        "member": "Team",
        "model": "Logistic Regression (baseline)",
        "import_train": "train_logistic_regression",
        "subset_note": "25% train data, same test set as everyone else",
        "extra_importance": False,
        "train_warning": "this ones quick",
    },
]


def md_cell(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.split("\n")}


def code_cell(text):
    lines = text.strip("\n").split("\n")
    # jupyter wants each line to end with \n except maybe last
    source = [line + "\n" for line in lines[:-1]] + [lines[-1]]
    return {"cell_type": "code", "metadata": {}, "outputs": [], "execution_count": None, "source": source}


def build_notebook(info):
    cells = []

    cells.append(md_cell(f"""# {info['title']}

my bit of the CloudGuard-IDS project (H9CML)

**me:** {info['member']}  
**model:** {info['model']}

### research questions (same for whole team)
- **RQ1:** can ML tell benign vs attack traffic on CICIDS 2017?
- **RQ2:** which model is best for AWS if we care about F1 and speed?

run `preprocess.py` + `make_subsets.py` before this notebook or it wont work.

{info['subset_note']}"""))

    cells.append(code_cell("""# path setup so imports work from notebooks folder
import sys
from pathlib import Path

ROOT = Path.cwd()
if not (ROOT / 'config.py').exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
%matplotlib inline

import utils
import notebook_utils as nb
import config"""))

    cells.append(md_cell("## load data"))


    cells.append(code_cell(f"""import {info['import_train']} as trainer

data = utils.load_data(subset=trainer.SUBSET)
print(f"Training rows: {{len(data['x_train']):,}}")
print(f"Test rows: {{len(data['x_test']):,}}")
print(f"Features: {{len(data['features'])}}")"""))

    cells.append(md_cell(f"""## train

{info['train_warning']}""".strip()))

    cells.append(code_cell("""print("training...")
metrics = trainer.train()
print("done")"""))

    cells.append(md_cell("## results"))


    cells.append(code_cell("""# reload model and metrics
import joblib
import json

model = joblib.load(config.MODELS_DIR / trainer.MODEL_NAME / 'model.joblib')
with open(config.MODELS_DIR / trainer.MODEL_NAME / 'metrics.json') as f:
    metrics = json.load(f)

nb.show_metrics(metrics)"""))

    cells.append(code_cell("nb.show_classification_report(model, data)"))

    cells.append(md_cell("## charts (for demo video)"))


    cells.append(code_cell(f"""nb.plot_confusion(model, data, title="{info['model']} - Confusion Matrix")"""))

    cells.append(code_cell(f"""nb.plot_roc(model, data, title="{info['model']} - ROC Curve")"""))

    if info["extra_importance"]:
        cells.append(code_cell(f"""nb.plot_feature_importance(model, data, title="{info['model']} - Important Features")"""))

    cells.append(code_cell("""nb.plot_errors_by_attack(model, data)"""))

    cells.append(md_cell(f"""## done

trained {info['model']}, charts above are what you show in the 4 min video.

model saved in `models/{info['import_train'].replace('train_', '')}/`"""))

    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.9.0",
            },
        },
        "cells": cells,
    }


def build_team_notebook():
    cells = [
        md_cell("""# team notebook

compare everyones models - run train_all.py first or theres nothing to show"""),

        code_cell("""import sys
from pathlib import Path

ROOT = Path.cwd()
if not (ROOT / 'config.py').exists():
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
%matplotlib inline

import pandas as pd
import json
import config"""),

        md_cell("## comparison table"),

        code_cell("""from IPython.display import display

rows = []
for name in ['random_forest', 'svm', 'neural_network', 'gradient_boosting', 'logistic_regression']:
    path = config.MODELS_DIR / name / 'metrics.json'
    if path.exists():
        with open(path) as f:
            m = json.load(f)
        rows.append({
            'Model': name,
            'Accuracy': m['accuracy'],
            'F1': m['f1'],
            'Recall': m['recall'],
            'Latency (ms)': m['latency_ms'],
        })

if not rows:
    print('No models trained yet - run train_all.py first')
else:
    df = pd.DataFrame(rows).sort_values('F1', ascending=False)
    display(df)"""),

        md_cell("## graphs from visualize.py"),

        code_cell("""from IPython.display import Image, display

fig_dir = config.DATA_DIR / 'reports' / 'figures'
for img in ['comparison_metrics.png', 'comparison_latency.png', 'comparison_roc.png']:
    path = fig_dir / img
    if path.exists():
        display(Image(filename=str(path)))
    else:
        print(f'Missing {img} - run python visualize.py')"""),

        md_cell("## who did what"),

        code_cell("""from IPython.display import display

team = pd.DataFrame([
    {'Member': 'Nikhil', 'Model': 'Random Forest', 'Notebook': 'random_forest.ipynb'},
    {'Member': 'Ishan', 'Model': 'SVM', 'Notebook': 'svm.ipynb'},
    {'Member': 'Aman', 'Model': 'Neural Network', 'Notebook': 'neural_network.ipynb'},
    {'Member': 'Ajay', 'Model': 'Gradient Boosting', 'Notebook': 'gradient_boosting.ipynb'},
    {'Member': 'Team', 'Model': 'Logistic Regression', 'Notebook': 'logistic_regression.ipynb'},
])
display(team)"""),
    ]

    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.9.0"},
        },
        "cells": cells,
    }


def main():
    out_dir = Path(__file__).parent / "notebooks"
    out_dir.mkdir(exist_ok=True)

    for info in NOTEBOOKS:
        path = out_dir / info["file"]
        with open(path, "w") as f:
            json.dump(build_notebook(info), f, indent=1)
        print(f"Created {path}")

    team_path = out_dir / "team_run_all.ipynb"
    with open(team_path, "w") as f:
        json.dump(build_team_notebook(), f, indent=1)
    print(f"Created {team_path}")


if __name__ == "__main__":
    main()
