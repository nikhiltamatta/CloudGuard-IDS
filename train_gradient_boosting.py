# Ajay's model - gradient boosting
# using HistGradientBoostingClassifier cause its faster than the normal one

from sklearn.ensemble import HistGradientBoostingClassifier
import utils
import config

MODEL_NAME = "gradient_boosting"

PARAMS = {
    "learning_rate": 0.1,
    "max_depth": 8,          # went higher and it overfit
    "max_iter": 200,
    "min_samples_leaf": 20,
    "random_state": config.RANDOM_STATE,
}

SUBSET = "train_100pct"


def train(subset=SUBSET, save_to=None):
    data = utils.load_data(subset=subset)
    model = HistGradientBoostingClassifier(**PARAMS)

    print(f"training GB on {len(data['x_train']):,} rows...")
    model.fit(data["x_train"], data["y_train"])

    out = save_to or (config.MODELS_DIR / MODEL_NAME)
    metrics = utils.get_metrics(model, data, MODEL_NAME)
    utils.save_model(model, metrics, MODEL_NAME, out_dir=out)
    utils.save_errors(model, data, MODEL_NAME, out_dir=out)
    return metrics


if __name__ == "__main__":
    train()
