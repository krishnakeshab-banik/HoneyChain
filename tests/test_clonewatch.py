from __future__ import annotations

from fastapi.testclient import TestClient


def _package(client: TestClient, post_reading) -> None:
    post_reading()
    client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-CW",
            "hive_id": "IN-WB-001",
            "beekeeper_id": "BK-WB-01",
            "harvested_at": "2026-09-14T12:00:00+00:00",
            "raw_weight_kg": 6.0,
            "moisture_pct": 17.0,
        },
    )
    client.post(
        "/api/batches",
        json={
            "batch_id": "BT-CW",
            "harvest_ids": ["HV-CW"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pass",
        },
    )
    client.post("/api/batches/BT-CW/commit")
    client.post("/api/packages", json={"package_id": "PK-CW", "batch_id": "BT-CW"})


def test_distant_scans_are_flagged(client: TestClient, post_reading) -> None:
    _package(client, post_reading)
    first = client.post(
        "/api/verify/PK-CW",
        json={
            "latitude": 22.5726,
            "longitude": 88.3639,
            "location_label": "Kolkata shop",
        },
    )
    assert first.status_code == 200
    assert first.json()["scan_flagged"] is False

    second = client.post(
        "/api/verify/PK-CW",
        json={
            "latitude": 53.0793,
            "longitude": 8.8017,
            "location_label": "Bremen store",
        },
    )
    assert second.status_code == 200
    assert second.json()["scan_flagged"] is True
    assert "km" in second.json()["scan_flag_reason"]

    report = client.get("/api/clonewatch")
    assert report.status_code == 200
    assert report.json()["flagged_scans"] >= 1
    assert any(
        item["kind"] == "anomalous_scan" and item["reference_id"] == "PK-CW"
        for item in report.json()["flagged_items"]
    )


def test_clonewatch_empty_when_clean(client: TestClient) -> None:
    report = client.get("/api/clonewatch")
    assert report.status_code == 200
    assert report.json()["flagged_items"] == []
