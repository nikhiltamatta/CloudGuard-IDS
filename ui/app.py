# DEPRECATED — use the Flask demo instead:
#   python3 run_demo.py
#   -> http://localhost:8000
#
# This Streamlit UI is kept only as a leftover. Local + AWS both use application.py.

import streamlit as st

st.set_page_config(page_title="CloudGuard-IDS (deprecated)", layout="wide")
st.title("CloudGuard-IDS — deprecated Streamlit UI")
st.warning(
    "This Streamlit app is no longer the project demo. "
    "Run `python3 run_demo.py` to open the Flask UI (same as Elastic Beanstalk)."
)
