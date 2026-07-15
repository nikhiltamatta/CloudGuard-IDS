# lightweight Lambda inference handler (no pandas dependency)

import csv
import json
import time
from pathlib import Path

import joblib

ROOT = Path(__file__).parent
DEFAULT_MODEL = "logistic_regression"


def predict(record, model_name=DEFAULT_MODEL):
    with open(ROOT / "data/processed/feature_columns.csv", newline="") as f:
        features = [row["feature"] for row in csv.DictReader(f)]

    row = [[float(record.get(f, 0.0)) for f in features]]
    model = joblib.load(ROOT / "models" / model_name / "model.joblib")

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
