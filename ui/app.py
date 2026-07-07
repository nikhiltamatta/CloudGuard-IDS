# streamlit app for demo / viva
# python run_demo.py to start

import json

import pandas as pd
import streamlit as st

import config
from predict import predict

FIGURES = config.DATA_DIR / "reports" / "figures"

MODELS = {
    "Random Forest (Nikhil)": "random_forest",
    "SVM (Ishan)": "svm",
    "Neural Network (Aman)": "neural_network",
    "Gradient Boosting (Ajay)": "gradient_boosting",
    "Logistic Regression (baseline)": "logistic_regression",
}

st.set_page_config(page_title="CloudGuard-IDS", layout="wide")
st.title("CloudGuard-IDS")
st.caption("our H9CML project - intrusion detection on CICIDS 2017")

st.write("**RQ1:** can ML spot attacks vs benign traffic?")
st.write("**RQ2:** which model is best for AWS (f1 vs speed)?")

tab1, tab2, tab3 = st.tabs(["my model", "compare everyone", "try a prediction"])

with tab1:
    choice = st.selectbox("model", list(MODELS.keys()))
    model_id = MODELS[choice]

    mf = config.MODELS_DIR / model_id / "metrics.json"
    if mf.exists():
        m = json.loads(mf.read_text())
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("accuracy", f"{m['accuracy']:.3f}")
        c2.metric("f1", f"{m['f1']:.3f}")
        c3.metric("recall", f"{m['recall']:.3f}")
        c4.metric("latency ms", f"{m['latency_ms']}")
    else:
        st.warning("not trained yet - run your train script first")

    for plot in ["confusion", "roc"]:
        img = FIGURES / f"{model_id}_{plot}.png"
        if img.exists():
            st.image(str(img))

with tab2:
    comp = config.DATA_DIR / "reports" / "model_comparison.csv"
    if comp.exists():
        st.dataframe(pd.read_csv(comp))
    else:
        st.info("run compare_models.py first")

    for img in ["comparison_metrics.png", "comparison_latency.png", "comparison_roc.png"]:
        p = FIGURES / img
        if p.exists():
            st.image(str(p))

with tab3:
    st.write("enter some flow features (rest default to 0)")
    mc = st.selectbox("pick model", list(MODELS.keys()), key="p")
    mid = MODELS[mc]

    port = st.number_input("destination port", value=80)
    dur = st.number_input("flow duration", value=120.0)
    fwd = st.number_input("fwd packets", value=10)
    bwd = st.number_input("bwd packets", value=8)

    if st.button("classify"):
        r = predict({
            "Destination Port": port,
            "Flow Duration": dur,
            "Total Fwd Packets": fwd,
            "Total Backward Packets": bwd,
        }, model_name=mid)
        st.success(f"{r['prediction']}  ({r['latency_ms']} ms)")
