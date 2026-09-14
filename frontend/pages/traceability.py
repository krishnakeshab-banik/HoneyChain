from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from frontend.api_client import api_get, api_send


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def render() -> None:
    st.title("Traceability")
    st.caption(
        "Purpose: register a harvest, assemble a batch, run the weight "
        "oracle, commit a passing batch to the hash-chain, and issue a package QR."
    )

    hives = api_get("/api/hives") or []
    keepers = api_get("/api/beekeepers") or []
    harvests = api_get("/api/harvests") or []
    batches = api_get("/api/batches") or []
    packages = api_get("/api/packages") or []
    chain = api_get("/api/ledger/chain") or []
    integrity = api_get("/api/ledger/integrity")

    if not hives or not keepers:
        st.warning("Hives or beekeepers are missing. Start the backend so seed data can load.")
        return

    st.subheader("1. Register a harvest")
    st.write(
        "Requires at least one sensor reading for the hive. "
        "Extracted weight cannot exceed the latest hive scale reading."
    )
    with st.form("harvest_form"):
        harvest_id = st.text_input("Harvest ID", value="HV-DEMO-001")
        hive = st.selectbox(
            "Hive",
            hives,
            format_func=lambda item: f"{item['hive_id']} · {item['name']}",
        )
        keeper = st.selectbox(
            "Beekeeper",
            keepers,
            format_func=lambda item: f"{item['beekeeper_id']} · {item['name']}",
        )
        raw_weight = st.number_input("Raw harvest weight (kg)", min_value=0.1, max_value=40.0, value=6.5)
        moisture = st.number_input("Moisture %", min_value=0.0, max_value=30.0, value=17.2)
        submitted = st.form_submit_button("Create harvest")
    if submitted:
        created = api_send(
            "POST",
            "/api/harvests",
            {
                "harvest_id": harvest_id,
                "hive_id": hive["hive_id"],
                "beekeeper_id": keeper["beekeeper_id"],
                "harvested_at": _ts(),
                "raw_weight_kg": raw_weight,
                "moisture_pct": moisture,
            },
        )
        if created:
            st.success(f"Harvest {created['harvest_id']} stored. Sensor-logged weight {created['sensor_logged_weight_kg']} kg.")
            st.rerun()

    if harvests:
        st.dataframe(pd.DataFrame(harvests), use_container_width=True)
    else:
        st.info("No harvests yet. Create one after the simulator has sent readings.")

    st.subheader("2. Create and commit a batch")
    harvest_ids = [item["harvest_id"] for item in harvests]
    with st.form("batch_form"):
        batch_id = st.text_input("Batch ID", value="BT-DEMO-001")
        selected_harvests = st.multiselect("Linked harvests", harvest_ids)
        declared = st.number_input(
            "Declared batch weight (kg)",
            min_value=0.1,
            max_value=200.0,
            value=6.5,
            help="Must stay within 10% of the summed sensor-logged harvest weights.",
        )
        lab = st.selectbox("Lab test result", ["pass", "fail", "pending"])
        notes = st.text_input("Lab notes", value="Moisture and HMF within spec.")
        create_clicked = st.form_submit_button("Create draft batch")
    if create_clicked:
        created = api_send(
            "POST",
            "/api/batches",
            {
                "batch_id": batch_id,
                "harvest_ids": selected_harvests,
                "processing_date": _ts(),
                "declared_weight_kg": declared,
                "lab_test_result": lab,
                "lab_notes": notes,
            },
        )
        if created:
            st.success(f"Draft batch {created['batch_id']} created.")
            st.rerun()

    if batches:
        st.dataframe(pd.DataFrame(batches).drop(columns=["harvests"], errors="ignore"), use_container_width=True)
        commit_id = st.selectbox(
            "Commit batch",
            [item["batch_id"] for item in batches if item["status"] != "committed"],
            index=None,
            placeholder="Select a draft or rejected batch to retry",
        )
        if st.button("Run oracle and commit", disabled=commit_id is None):
            result = api_send("POST", f"/api/batches/{commit_id}/commit")
            if result:
                st.success(f"Batch {result['batch_id']} committed. {result['oracle_reason']}")
                st.rerun()
    else:
        st.info("No batches yet.")

    st.subheader("3. Issue a package QR")
    committed = [item["batch_id"] for item in batches if item["status"] == "committed"]
    with st.form("package_form"):
        package_id = st.text_input("Package ID", value="PK-DEMO-001")
        batch_choice = st.selectbox("Committed batch", committed, index=0 if committed else None)
        issued = st.form_submit_button("Generate package + QR", disabled=not committed)
    if issued and batch_choice:
        created = api_send(
            "POST",
            "/api/packages",
            {"package_id": package_id, "batch_id": batch_choice},
        )
        if created:
            st.success(f"Package {created['package_id']} ready. Scan URL: {created['qr_reference']}")
            st.rerun()

    if packages:
        st.dataframe(pd.DataFrame(packages), use_container_width=True)
        for package in packages:
            st.image(
                f"http://127.0.0.1:8000/api/packages/{package['package_id']}/qr",
                caption=package["qr_reference"],
                width=180,
            )
    else:
        st.info("No packages yet. Commit a passing batch first.")

    st.subheader("Ledger")
    if integrity:
        if integrity["valid"]:
            st.success(integrity["detail"])
        else:
            st.error(integrity["detail"])
    if chain:
        st.dataframe(pd.DataFrame(chain), use_container_width=True)
    else:
        st.info("Ledger is empty until a batch passes the oracle and is committed.")
