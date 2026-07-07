# Aman's model - basic MLP with 2 hidden layers
# not a deep learning model just sklearn's MLPClassifier

from sklearn.neural_network import MLPClassifier
import utils
import config

MODEL_NAME = "neural_network"

PARAMS = {
    "hidden_layer_sizes": (128, 64),
    "activation": "relu",
    "solver": "adam",
    "alpha": 0.0001,
    "batch_size": 256,
    "learning_rate_init": 0.001,
    "max_iter": 30,
    "early_stopping": True,   # stops early if val score stops improving
    "random_state": config.RANDOM_STATE,
}

SUBSET = "train_100pct"


def train(subset=SUBSET, save_to=None):
    data = utils.load_data(subset=subset)
    model = MLPClassifier(**PARAMS)

    print(f"training NN on {len(data['x_train']):,} rows...")
    model.fit(data["x_train"], data["y_train"])

    if hasattr(model, "n_iter_"):
        print(f"finished at iteration {model.n_iter_}")

    out = save_to or (config.MODELS_DIR / MODEL_NAME)
    metrics = utils.get_metrics(model, data, MODEL_NAME)
    utils.save_model(model, metrics, MODEL_NAME, out_dir=out)
    utils.save_errors(model, data, MODEL_NAME, out_dir=out)
    return metrics


if __name__ == "__main__":
    train()
