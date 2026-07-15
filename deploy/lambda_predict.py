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


def _response(status_code, payload):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload),
    }


def lambda_handler(event, context=None):
    method = (event.get("httpMethod") or "POST").upper()

    # browser opens use GET — return a health/help payload instead of prediction
    if method == "GET":
        return _response(
            200,
            {
                "status": "ok",
                "service": "cloudguard-ids-predict",
                "default_model": DEFAULT_MODEL,
                "usage": {
                    "method": "POST",
                    "content_type": "application/json",
                    "example_body": {
                        "Destination Port": 80,
                        "Flow Duration": 120,
                        "Total Fwd Packets": 10,
                        "model": DEFAULT_MODEL,
                    },
                },
            },
        )

    if method != "POST":
        return _response(405, {"error": "Use GET for health check or POST for prediction"})

    body = event.get("body") or "{}"
    if isinstance(body, str):
        body = json.loads(body or "{}")

    model_name = body.get("model", DEFAULT_MODEL)
    result = predict(body, model_name=model_name)
    return _response(200, result)
