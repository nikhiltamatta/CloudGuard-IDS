# baseline model - logistic regression
# everyone compares against this, should be quick to train

from sklearn.linear_model import LogisticRegression
import utils
import config

MODEL_NAME = "logistic_regression"

PARAMS = {
    "C": 1.0,
    "class_weight": "balanced",
    "max_iter": 1000,
    "solver": "lbfgs",
    "random_state": config.RANDOM_STATE,
}

SUBSET = "train_25pct"  # fast enough, same test set anyway


def train(subset=SUBSET, save_to=None):
    data = utils.load_data(subset=subset)
    model = LogisticRegression(**PARAMS)

    print(f"training logistic regression on {len(data['x_train']):,} rows...")
    model.fit(data["x_train"], data["y_train"])

    out = save_to or (config.MODELS_DIR / MODEL_NAME)
    metrics = utils.get_metrics(model, data, MODEL_NAME)
    utils.save_model(model, metrics, MODEL_NAME, out_dir=out)
    utils.save_errors(model, data, MODEL_NAME, out_dir=out)
    return metrics


if __name__ == "__main__":
    train()
