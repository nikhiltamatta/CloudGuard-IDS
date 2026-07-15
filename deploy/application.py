# Flask app for Elastic Beanstalk (no WebSocket required)

import json
from pathlib import Path

import pandas as pd
from flask import Flask, render_template_string, request

import config
from predict import predict

app = Flask(__name__)

MODELS = {
    "Random Forest (Nikhil)": "random_forest",
    "SVM (Ishan)": "svm",
    "Neural Network (Aman)": "neural_network",
    "Gradient Boosting (Ajay)": "gradient_boosting",
    "Logistic Regression (baseline)": "logistic_regression",
}

FIGURES = config.DATA_DIR / "reports" / "figures"

PAGE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>CloudGuard-IDS</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2rem; background: #0e1117; color: #fafafa; }
    h1, h2 { color: #ffffff; }
    .card { background: #262730; padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 1rem; }
    .metrics { display: flex; gap: 1rem; flex-wrap: wrap; }
    .metric { background: #1b1d24; padding: 0.75rem 1rem; border-radius: 6px; min-width: 120px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid #444; padding: 0.5rem; text-align: left; }
    img { max-width: 100%; margin: 0.5rem 0; border-radius: 6px; }
    select, input, button { padding: 0.5rem; margin: 0.25rem 0; }
    .success { color: #6eff8b; font-weight: bold; }
    .warn { color: #ffd166; }
    a { color: #7ab7ff; margin-right: 1rem; }
  </style>
</head>
<body>
  <h1>CloudGuard-IDS</h1>
  <p>our H9CML project - intrusion detection on CICIDS 2017</p>
  <p><strong>RQ1:</strong> can ML spot attacks vs benign traffic?</p>
  <p><strong>RQ2:</strong> which model is best for AWS (f1 vs speed)?</p>
  <p>
    <a href="/?tab=model">my model</a>
    <a href="/?tab=compare">compare everyone</a>
    <a href="/?tab=predict">try a prediction</a>
  </p>

  {% if tab == 'model' %}
  <div class="card">
    <h2>My model</h2>
    <form method="get">
      <input type="hidden" name="tab" value="model">
      <label>model</label>
      <select name="model" onchange="this.form.submit()">
        {% for label, mid in models.items() %}
        <option value="{{ mid }}" {% if mid == selected_model %}selected{% endif %}>{{ label }}</option>
        {% endfor %}
      </select>
    </form>
    {% if metrics %}
    <div class="metrics">
      <div class="metric"><div>accuracy</div><strong>{{ metrics.accuracy }}</strong></div>
      <div class="metric"><div>f1</div><strong>{{ metrics.f1 }}</strong></div>
      <div class="metric"><div>recall</div><strong>{{ metrics.recall }}</strong></div>
      <div class="metric"><div>latency ms</div><strong>{{ metrics.latency_ms }}</strong></div>
    </div>
    {% else %}
    <p class="warn">metrics not found for this model</p>
    {% endif %}
    {% for plot in plots %}
    <img src="/figures/{{ plot }}" alt="{{ plot }}">
    {% endfor %}
  </div>
  {% endif %}

  {% if tab == 'compare' %}
  <div class="card">
    <h2>Compare everyone</h2>
    {% if comparison_html %}
    {{ comparison_html|safe }}
    {% else %}
    <p class="warn">comparison table not available</p>
    {% endif %}
    {% for plot in compare_plots %}
    <img src="/figures/{{ plot }}" alt="{{ plot }}">
    {% endfor %}
  </div>
  {% endif %}

  {% if tab == 'predict' %}
  <div class="card">
    <h2>Try a prediction</h2>
    <form method="post">
      <input type="hidden" name="tab" value="predict">
      <label>model</label>
      <select name="model">
        {% for label, mid in models.items() %}
        <option value="{{ mid }}" {% if mid == selected_model %}selected{% endif %}>{{ label }}</option>
        {% endfor %}
      </select><br>
      <label>destination port</label><input name="port" value="{{ port }}"><br>
      <label>flow duration</label><input name="duration" value="{{ duration }}"><br>
      <label>fwd packets</label><input name="fwd" value="{{ fwd }}"><br>
      <label>bwd packets</label><input name="bwd" value="{{ bwd }}"><br>
      <button type="submit">classify</button>
    </form>
    {% if result %}
    <p class="success">{{ result.prediction }} ({{ result.latency_ms }} ms)</p>
    {% endif %}
  </div>
  {% endif %}
</body>
</html>
"""


def _load_metrics(model_id):
    path = config.MODELS_DIR / model_id / "metrics.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


@app.route("/health")
def health():
    return "ok"


@app.route("/figures/<path:filename>")
def figures(filename):
    from flask import send_from_directory
    return send_from_directory(FIGURES, filename)


@app.route("/", methods=["GET", "POST"])
def index():
    tab = request.values.get("tab", "model")
    selected_model = request.values.get("model", "random_forest")

    metrics = _load_metrics(selected_model) if tab == "model" else None
    plots = []
    if tab == "model":
        for name in [f"{selected_model}_confusion.png", f"{selected_model}_roc.png"]:
            if (FIGURES / name).exists():
                plots.append(name)

    comparison_html = None
    compare_plots = []
    if tab == "compare":
        comp = config.DATA_DIR / "reports" / "model_comparison.csv"
        if comp.exists():
            comparison_html = pd.read_csv(comp).to_html(index=False)
        for name in ["comparison_metrics.png", "comparison_latency.png", "comparison_roc.png"]:
            if (FIGURES / name).exists():
                compare_plots.append(name)

    result = None
    port = request.values.get("port", "80")
    duration = request.values.get("duration", "120.0")
    fwd = request.values.get("fwd", "10")
    bwd = request.values.get("bwd", "8")

    if tab == "predict" and request.method == "POST":
        selected_model = request.form.get("model", selected_model)
        result = predict({
            "Destination Port": float(port),
            "Flow Duration": float(duration),
            "Total Fwd Packets": float(fwd),
            "Total Backward Packets": float(bwd),
        }, model_name=selected_model)

    return render_template_string(
        PAGE,
        tab=tab,
        models=MODELS,
        selected_model=selected_model,
        metrics=metrics,
        plots=plots,
        comparison_html=comparison_html,
        compare_plots=compare_plots,
        result=result,
        port=port,
        duration=duration,
        fwd=fwd,
        bwd=bwd,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
