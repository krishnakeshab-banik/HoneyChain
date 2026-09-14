from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.api_client import api_get


def _hive_options() -> list[dict[str, Any]]:
    hives = api_get("/api/hives")
    return hives or []


@st.fragment(run_every="5s")
def render_live_overview(hive_id: str) -> None:
    summary = api_get(f"/api/hives/{hive_id}/summary")
    hive = api_get(f"/api/hives/{hive_id}")
    if summary is None:
        return
    latest = summary.get("latest")
    if latest is None:
        st.warning(
            "This hive is registered, but no telemetry has arrived yet. "
            "Start the simulator."
        )
        return

    st.markdown('<span class="live-badge">● LIVE SIMULATION</span>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">CURRENT HIVE STATE</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Inside temperature", f"{latest['inside_temperature_c']:.1f} °C")
    col2.metric("Humidity", f"{latest['humidity_pct']:.1f} %")
    col3.metric("Hive weight", f"{latest['weight_kg']:.2f} kg")
    col4.metric("Readings received", summary["reading_count"])

    if hive:
        source = "Simulated demonstration telemetry"
        if hive["data_source"] == "real_dataset":
            source = f"Real dataset · {hive['source_reference']}"
        st.markdown('<div class="section-label">ACTIVE HIVE</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="status-card">
            <b>{hive['name']}</b><br>
            <span style="color:#777;">
            {hive['hive_id']} · {hive['bee_species']} · {hive['climate_zone']}
            </span>
            <br><br>
            <span style="color:#9A6A16;">● {source}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.caption(f"Latest telemetry received: {latest['timestamp']}")


def render() -> None:
    st.markdown('<div class="brand">HONEYCHAIN</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title">From hive signals to trusted honey.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-subtitle">
        Live hive telemetry, harvest-to-package traceability, and a
        hash-chain check that is recomputed on every verification.
        </div>
        """,
        unsafe_allow_html=True,
    )

    hives = _hive_options()
    if not hives:
        st.info("No hives are registered yet.")
        return

    default_index = 0
    for index, hive in enumerate(hives):
        if hive["hive_id"] == "IN-WB-001":
            default_index = index
            break
    selected = st.selectbox(
        "Hive",
        options=hives,
        index=default_index,
        format_func=lambda item: f"{item['hive_id']} · {item['name']}",
    )
    render_live_overview(selected["hive_id"])
