from __future__ import annotations

import pandas as pd
import streamlit as st

from frontend.api_client import api_get


def render() -> None:
    st.title("CloneWatch")
    st.caption(
        "Purpose: list every oracle rejection and every flagged consumer "
        "scan, each with the specific reason. This page is empty only when "
        "nothing has been flagged yet — not because the module is unfinished."
    )

    report = api_get("/api/clonewatch")
    if report is None:
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Flagged items", len(report["flagged_items"]))
    col2.metric("Oracle failures", report["oracle_failures"])
    col3.metric("Anomalous scans", report["flagged_scans"])

    if not report["flagged_items"]:
        st.info(
            "No flags yet. Commit a batch with a weight that is more than "
            "10% off the harvest sum, or verify the same package from "
            "Kolkata and Bremen within two hours."
        )
        return

    rows = []
    for item in report["flagged_items"]:
        rows.append(
            {
                "kind": item["kind"],
                "reference": item["reference_id"],
                "reason": item["reason"],
                "recorded_at": item["recorded_at"],
                **{str(key): value for key, value in item["extra"].items()},
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True)
