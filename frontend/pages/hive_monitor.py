from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from frontend.api_client import api_get


def _selected_hive() -> dict[str, Any] | None:
    hives = api_get("/api/hives") or []
    if not hives:
        st.info("No hives are registered yet.")
        return None
    default_index = 0
    for index, hive in enumerate(hives):
        if hive["hive_id"] == "IN-WB-001":
            default_index = index
            break
    return st.selectbox(
        "Hive",
        options=hives,
        index=default_index,
        format_func=lambda item: f"{item['hive_id']} · {item['name']}",
        key="monitor_hive",
    )


@st.fragment(run_every="5s")
def render_live_monitor(hive_id: str) -> None:
    readings = api_get(f"/api/hives/{hive_id}/sensor-readings")
    if readings is None:
        return
    if len(readings) == 0:
        st.warning("No telemetry available yet. Start the hive simulator.")
        return

    df = pd.DataFrame(readings)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    latest = df.iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("Latest inside temperature", f"{latest['inside_temperature_c']:.1f} °C")
    col2.metric("Latest humidity", f"{latest['humidity_pct']:.1f} %")
    col3.metric("Telemetry points", len(df))

    temperature_figure = px.line(
        df,
        x="timestamp",
        y=["inside_temperature_c", "outside_temperature_c"],
        title="Temperature telemetry",
    )
    temperature_figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Temperature (°C)",
        legend_title="Signal",
        margin=dict(l=20, r=20, t=55, b=20),
    )
    st.plotly_chart(temperature_figure, use_container_width=True)

    humidity_figure = px.line(df, x="timestamp", y="humidity_pct", title="Hive humidity")
    humidity_figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Relative humidity (%)",
        margin=dict(l=20, r=20, t=55, b=20),
    )
    st.plotly_chart(humidity_figure, use_container_width=True)

    weight_figure = px.line(df, x="timestamp", y="weight_kg", title="Hive weight")
    weight_figure.update_layout(
        xaxis_title="Time",
        yaxis_title="Weight (kg)",
        margin=dict(l=20, r=20, t=55, b=20),
    )
    st.plotly_chart(weight_figure, use_container_width=True)

    with st.expander("View raw telemetry"):
        st.dataframe(df, use_container_width=True)


def render() -> None:
    st.title("Hive Monitor")
    st.caption(
        "Purpose: watch live simulated sensor streams. Charts refresh every "
        "five seconds from SQLite-backed API history."
    )
    hive = _selected_hive()
    if hive is None:
        return
    render_live_monitor(hive["hive_id"])
