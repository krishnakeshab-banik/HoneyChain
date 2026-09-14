"""Full journey: telemetry → harvest → oracle → ledger → QR → scan → flag."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_full_traceability_journey(client: TestClient, post_reading) -> None:
    post_reading(hive_id="IN-WB-001", weight_kg=42.8)
    post_reading(hive_id="DE-001", weight_kg=44.1)

    harvest = client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-E2E",
            "hive_id": "IN-WB-001",
            "beekeeper_id": "BK-WB-01",
            "harvested_at": "2026-09-14T12:00:00+00:00",
            "raw_weight_kg": 7.0,
            "moisture_pct": 16.8,
        },
    )
    assert harvest.status_code == 201, harvest.text

    batch = client.post(
        "/api/batches",
        json={
            "batch_id": "BT-E2E",
            "harvest_ids": ["HV-E2E"],
            "processing_date": "2026-09-14T16:00:00+00:00",
            "declared_weight_kg": 7.0,
            "lab_test_result": "pass",
            "lab_notes": "e2e",
        },
    )
    assert batch.status_code == 201
    committed = client.post("/api/batches/BT-E2E/commit")
    assert committed.status_code == 200
    assert committed.json()["oracle_status"] == "passed"

    integrity = client.get("/api/ledger/integrity")
    assert integrity.json()["valid"] is True

    package = client.post(
        "/api/packages",
        json={"package_id": "PK-E2E", "batch_id": "BT-E2E"},
    )
    assert package.status_code == 201
    qr = client.get("/api/packages/PK-E2E/qr")
    assert qr.status_code == 200

    verified = client.get("/api/verify/PK-E2E")
    assert verified.status_code == 200
    assert verified.json()["ledger_verified"] is True

    anomalous = client.post(
        "/api/verify/PK-E2E",
        json={
            "latitude": 53.0793,
            "longitude": 8.8017,
            "location_label": "Bremen store",
        },
    )
    assert anomalous.status_code == 200
    assert anomalous.json()["scan_flagged"] is True

    watch = client.get("/api/clonewatch")
    assert any(item["reference_id"] == "PK-E2E" for item in watch.json()["flagged_items"])

    fail = client.post(
        "/api/batches",
        json={
            "batch_id": "BT-E2E-BAD",
            "harvest_ids": ["HV-E2E"],
            "processing_date": "2026-09-14T17:00:00+00:00",
            "declared_weight_kg": 30.0,
            "lab_test_result": "pass",
        },
    )
    assert fail.status_code == 201
    assert client.post("/api/batches/BT-E2E-BAD/commit").status_code == 409
    watch2 = client.get("/api/clonewatch")
    assert any(item["reference_id"] == "BT-E2E-BAD" for item in watch2.json()["flagged_items"])
