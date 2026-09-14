from __future__ import annotations

from fastapi.testclient import TestClient


def _admin_headers(client: TestClient) -> dict[str, str]:
    token = client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _commit(client: TestClient, post_reading) -> None:
    post_reading()
    client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-TAMPER",
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
            "batch_id": "BT-TAMPER",
            "harvest_ids": ["HV-TAMPER"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pass",
        },
    )
    assert client.post("/api/batches/BT-TAMPER/commit").status_code == 200


def test_tamper_breaks_and_reset_restores(client: TestClient, post_reading) -> None:
    headers = _admin_headers(client)
    empty = client.post("/api/ledger/tamper-test", headers=headers)
    assert empty.status_code == 409

    denied = client.post("/api/ledger/tamper-test")
    assert denied.status_code == 401

    _commit(client, post_reading)
    ok = client.get("/api/ledger/integrity")
    assert ok.json()["valid"] is True

    broken = client.post("/api/ledger/tamper-test", headers=headers)
    assert broken.status_code == 200, broken.text
    body = broken.json()
    assert body["action"] == "tamper"
    assert body["stored_weight_kg"] != body["committed_weight_kg"]
    assert body["integrity"]["valid"] is False
    assert body["integrity"]["failed_index"] is not None
    assert body["integrity"]["broken_indexes"]

    live = client.get("/api/ledger/integrity")
    assert live.json()["valid"] is False

    restored = client.post("/api/ledger/tamper-reset", headers=headers)
    assert restored.status_code == 200
    assert restored.json()["integrity"]["valid"] is True
    assert client.get("/api/ledger/integrity").json()["valid"] is True


def test_officer_cannot_tamper(client: TestClient, post_reading) -> None:
    _commit(client, post_reading)
    token = client.post("/api/auth/login", json={"username": "officer", "password": "Officer123!"}).json()["access_token"]
    response = client.post("/api/ledger/tamper-test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
