# Ishan's model - Linear SVM
# only using 25% of train data because full set literally took 40+ mins on my laptop

from sklearn.svm import LinearSVC
import utils
import config

MODEL_NAME = "svm"

PARAMS = {
    "C": 1.0,
    "class_weight": "balanced",
    "dual": False,        # read online this is faster when n_samples > n_features
    "max_iter": 5000,
    "random_state": config.RANDOM_STATE,
}

SUBSET = "train_25pct"


def train(subset=SUBSET, save_to=None):
    data = utils.load_data(subset=subset)
    model = LinearSVC(**PARAMS)

    print(f"training SVM on {len(data['x_train']):,} rows...")
    print("go make coffee this ones slow")
    model.fit(data["x_train"], data["y_train"])

    out = save_to or (config.MODELS_DIR / MODEL_NAME)
    metrics = utils.get_metrics(model, data, MODEL_NAME)
    utils.save_model(model, metrics, MODEL_NAME, out_dir=out)
    utils.save_errors(model, data, MODEL_NAME, out_dir=out)
    return metrics


if __name__ == "__main__":
    train()
