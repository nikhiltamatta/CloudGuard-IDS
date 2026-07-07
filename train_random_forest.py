# Nikhil's model - Random Forest
# tried a few different n_estimators, 200 seemed ok

from sklearn.ensemble import RandomForestClassifier
import utils
import config

MODEL_NAME = "random_forest"

PARAMS = {
    "n_estimators": 200,       # 100 was a bit worse on val set
    "max_depth": 20,
    "min_samples_leaf": 2,
    "class_weight": "balanced_subsample",  # way more benign than attack rows
    "n_jobs": -1,              # use all cpu cores
    "random_state": config.RANDOM_STATE,
}

SUBSET = "train_100pct"  # trees like having more data


def train(subset=SUBSET, save_to=None):
    data = utils.load_data(subset=subset)
    model = RandomForestClassifier(**PARAMS)

    print(f"training RF on {len(data['x_train']):,} rows...")
    model.fit(data["x_train"], data["y_train"])

    out = save_to or (config.MODELS_DIR / MODEL_NAME)
    metrics = utils.get_metrics(model, data, MODEL_NAME)
    utils.save_model(model, metrics, MODEL_NAME, out_dir=out)
    utils.save_errors(model, data, MODEL_NAME, out_dir=out)
    return metrics


if __name__ == "__main__":
    train()
