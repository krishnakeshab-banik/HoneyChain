from __future__ import annotations

import streamlit as st

from frontend.api_client import api_get, api_send

DEMO_LOCATIONS: dict[str, dict[str, float | str]] = {
    "Kolkata shop": {"latitude": 22.5726, "longitude": 88.3639, "location_label": "Kolkata shop"},
    "Mumbai market": {"latitude": 19.0760, "longitude": 72.8777, "location_label": "Mumbai market"},
    "Bremen store": {"latitude": 53.0793, "longitude": 8.8017, "location_label": "Bremen store"},
}


def render() -> None:
    st.title("Consumer Honey Passport")
    st.caption(
        "Purpose: open a jar QR (or paste the package ID) and see beekeeper, "
        "harvest date, lab result, hive health at harvest, and a live "
        "recomputed ledger check. Each lookup is logged as a scan."
    )

    query_package = st.query_params.get("package_id", "")
    packages = api_get("/api/packages") or []
    known_ids = [item["package_id"] for item in packages]

    default_id = query_package or (known_ids[0] if known_ids else "")
    package_id = st.text_input("Package ID", value=default_id)
    location_name = st.selectbox(
        "Scan location (simulated)",
        list(DEMO_LOCATIONS.keys()),
        help="Locations are simulated. Used by CloneWatch distance checks.",
    )

    if not package_id:
        st.info("No package ID yet. Issue one on the Traceability page, or scan a generated QR.")
        return

    if st.button("Verify package", type="primary"):
        location = DEMO_LOCATIONS[location_name]
        passport = api_send("POST", f"/api/verify/{package_id}", location)
        if passport is None:
            return
        st.session_state["last_passport"] = passport

    passport = st.session_state.get("last_passport")
    if not passport:
        st.info("Press Verify package to run a live scan.")
        return

    if passport["ledger_verified"]:
        st.success(f"Ledger verified. {passport['ledger_detail']}")
    else:
        st.error(f"Ledger check failed. {passport['ledger_detail']}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Beekeeper", passport["beekeeper_name"])
    col2.metric("Cluster", passport["cluster"])
    col3.metric("Lab result", passport["lab_test_result"])

    st.write("Harvest dates")
    st.write(passport["harvest_dates"])
    st.write("Hive health at harvest")
    st.dataframe(passport["hive_health_at_harvest"], use_container_width=True)
    st.caption(f"QR target: {passport['qr_reference']}")
    if passport["scan_flagged"]:
        st.warning(f"This scan was flagged: {passport['scan_flag_reason']}")
    st.image(
        f"http://127.0.0.1:8000/api/packages/{passport['package_id']}/qr",
        caption="Generated QR — opening its URL lands back on this page with package_id set.",
        width=180,
    )
