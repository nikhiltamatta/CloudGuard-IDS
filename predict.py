# predict one network flow - used by streamlit + lambda
# missing features default to 0 which isnt perfect but ok for demo

import json
import time

import joblib
import pandas as pd

import config

DEFAULT_MODEL = "random_forest"


def predict(record, model_name=DEFAULT_MODEL):
    features = pd.read_csv(config.DATA_DIR / "feature_columns.csv")["feature"].tolist()
    row = pd.DataFrame([{f: float(record.get(f, 0.0)) for f in features}])

    model = joblib.load(config.MODELS_DIR / model_name / "model.joblib")

    t0 = time.time()
    result = int(model.predict(row)[0])
    ms = round((time.time() - t0) * 1000, 2)

    return {
        "prediction": "Attack" if result == 1 else "Benign",
        "label_code": result,
        "model": model_name,
        "latency_ms": ms,
    }


def lambda_handler(event, context=None):
    body = event.get("body", "{}")
    if isinstance(body, str):
        body = json.loads(body)

    model_name = body.get("model", DEFAULT_MODEL)
    result = predict(body, model_name=model_name)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result),
    }
