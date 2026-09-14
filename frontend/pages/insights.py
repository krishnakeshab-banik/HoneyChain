from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.api_client import api_get


def render() -> None:
    st.title("Insights")
    st.caption(
        "Purpose: show colony-health classification and a short-horizon "
        "weight forecast from scikit-learn models. Both models are trained "
        "on the inspected local MSPB D1/D2 table. Hive weight is this hive's scale, "
        "not MSPB honey kilograms."
    )

    hives = api_get("/api/hives") or []
    if not hives:
        st.info("No hives are registered yet.")
        return
    default_index = 0
    for index, hive in enumerate(hives):
        if hive["hive_id"] == "IN-WB-001":
            default_index = index
            break
    hive = st.selectbox(
        "Hive",
        hives,
        index=default_index,
        format_func=lambda item: f"{item['hive_id']} · {item['name']}",
        key="insights_hive",
    )

    insights = api_get(f"/api/insights/{hive['hive_id']}")
    if insights is None:
        st.info("Need at least five sensor readings before the models can run. Start the simulator.")
        return

    health = insights["health"]
    forecast = insights["forecast"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Colony status", health["status"])
    col2.metric("Model confidence", f"{health['confidence'] * 100:.1f}%")
    col3.metric("Forecast hive weight", f"{forecast['predicted_weight_kg']:.2f} kg")

    st.write(f"Health model: {health['model_name']}")
    st.caption(health["trained_on"])
    st.write(f"Forecast model: {forecast['model_name']}")
    st.caption(forecast["trained_on"])

    feature_df = pd.DataFrame(
        [{"feature": key, "value": value} for key, value in health["features"].items()]
    )
    figure = px.bar(feature_df, x="feature", y="value", title="Features fed to the models")
    figure.update_layout(xaxis_title="Feature", yaxis_title="Value")
    st.plotly_chart(figure, use_container_width=True)

    compare = pd.DataFrame(
        [
            {"series": "Latest measured weight", "kg": forecast["recent_weight_kg"]},
            {"series": "Forecast weight", "kg": forecast["predicted_weight_kg"]},
        ]
    )
    compare_fig = px.bar(compare, x="series", y="kg", title="Measured vs forecast hive weight")
    compare_fig.update_layout(xaxis_title="Series", yaxis_title="Weight (kg)")
    st.plotly_chart(compare_fig, use_container_width=True)
