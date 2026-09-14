"""
HoneyChain Prototype Dashboard
==============================

FILE:
    frontend/app.py

The original Overview and Hive Monitor behaviour is preserved: live
metrics and Plotly charts refresh every five seconds from the API.
Pages now live in frontend/pages/ so new product surfaces can be wired
without turning this file into a god-script.

The sidebar gained an Insights page because the ML module has a real
dashboard surface. That is an addition, not a change to the existing
Overview / Hive Monitor contracts.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from frontend.pages.clonewatch import render as render_clonewatch
from frontend.pages.consumer_verify import render as render_consumer_verify
from frontend.pages.hive_monitor import render as render_hive_monitor
from frontend.pages.insights import render as render_insights
from frontend.pages.overview import render as render_overview
from frontend.pages.traceability import render as render_traceability
from frontend.styles import apply_theme

st.set_page_config(
    page_title="HoneyChain",
    page_icon="🍯",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()

st.sidebar.markdown("## 🍯 HoneyChain")
st.sidebar.caption("Evidence-backed honey intelligence")
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<small style='color:#9A938A;'>OPERATOR PROTOTYPE</small>",
    unsafe_allow_html=True,
)

query_package = st.query_params.get("package_id")
nav_pages = [
    "Overview",
    "Hive Monitor",
    "Traceability",
    "Consumer Verify",
    "CloneWatch",
    "Insights",
]
default_page = "Consumer Verify" if query_package else "Overview"
page = st.sidebar.radio(
    "Navigate",
    nav_pages,
    index=nav_pages.index(default_page),
)

st.sidebar.markdown("---")
st.sidebar.caption("Prototype build · Hackathon 2026")

if page == "Overview":
    render_overview()
elif page == "Hive Monitor":
    render_hive_monitor()
elif page == "Traceability":
    render_traceability()
elif page == "Consumer Verify":
    render_consumer_verify()
elif page == "CloneWatch":
    render_clonewatch()
elif page == "Insights":
    render_insights()
