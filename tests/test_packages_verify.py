from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def _ready_package(client: TestClient, post_reading, package_id: str = "PK-001") -> str:
    post_reading()
    client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-PK",
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
            "batch_id": "BT-PK",
            "harvest_ids": ["HV-PK"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pass",
        },
    )
    assert client.post("/api/batches/BT-PK/commit").status_code == 200
    created = client.post(
        "/api/packages",
        json={"package_id": package_id, "batch_id": "BT-PK"},
    )
    assert created.status_code == 201, created.text
    return package_id


def test_package_qr_and_get_verify_url(client: TestClient, post_reading) -> None:
    package_id = _ready_package(client, post_reading)
    listed = client.get("/api/packages")
    assert listed.status_code == 200
    assert listed.json()[0]["package_id"] == package_id
    assert "/verify?package_id=" in listed.json()[0]["qr_reference"]

    qr = client.get(f"/api/packages/{package_id}/qr")
    assert qr.status_code == 200
    assert qr.headers["content-type"].startswith("image/png")
    assert Path(listed.json()[0]["qr_image_path"]).is_file()

    passport = client.get(f"/api/verify/{package_id}")
    assert passport.status_code == 200, passport.text
    body = passport.json()
    assert body["package_id"] == package_id
    assert body["ledger_verified"] is True
    assert body["beekeeper_name"] == "Ananya Roy"
    assert body["cluster"] == "West Bengal Producer Cluster"
    assert body["lab_test_result"] == "pass"
    assert body["hive_health_at_harvest"][0]["hive_id"] == "IN-WB-001"


def test_verify_unknown_package_404(client: TestClient) -> None:
    response = client.get("/api/verify/PK-NOPE")
    assert response.status_code == 404


def test_package_on_uncommitted_batch_409(client: TestClient, post_reading) -> None:
    post_reading()
    client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-DRAFT",
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
            "batch_id": "BT-DRAFT",
            "harvest_ids": ["HV-DRAFT"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pass",
        },
    )
    response = client.post(
        "/api/packages",
        json={"package_id": "PK-DRAFT", "batch_id": "BT-DRAFT"},
    )
    assert response.status_code == 409


def test_duplicate_package_409(client: TestClient, post_reading) -> None:
    _ready_package(client, post_reading, "PK-DUP")
    again = client.post(
        "/api/packages",
        json={"package_id": "PK-DUP", "batch_id": "BT-PK"},
    )
    assert again.status_code == 409


def test_get_missing_package_404(client: TestClient) -> None:
    assert client.get("/api/packages/NOPE").status_code == 404


def test_delete_package(client: TestClient, post_reading) -> None:
    _ready_package(client, post_reading, "PK-DEL")
    assert client.delete("/api/packages/PK-DEL").status_code == 204
    assert client.get("/api/packages/PK-DEL").status_code == 404
    assert client.delete("/api/packages/PK-DEL").status_code == 404
