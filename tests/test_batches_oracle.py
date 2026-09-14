from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient


def _harvest(client: TestClient, post_reading: Callable[..., None], harvest_id: str = "HV-B1") -> None:
    post_reading()
    response = client.post(
        "/api/harvests",
        json={
            "harvest_id": harvest_id,
            "hive_id": "IN-WB-001",
            "beekeeper_id": "BK-WB-01",
            "harvested_at": "2026-09-14T12:00:00+00:00",
            "raw_weight_kg": 6.0,
            "moisture_pct": 17.0,
        },
    )
    assert response.status_code == 201, response.text


def test_commit_batch_happy_path(client: TestClient, post_reading) -> None:
    _harvest(client, post_reading)
    created = client.post(
        "/api/batches",
        json={
            "batch_id": "BT-OK",
            "harvest_ids": ["HV-B1"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pass",
            "lab_notes": "ok",
        },
    )
    assert created.status_code == 201, created.text
    committed = client.post("/api/batches/BT-OK/commit")
    assert committed.status_code == 200, committed.text
    assert committed.json()["status"] == "committed"
    assert committed.json()["oracle_status"] == "passed"


def test_oracle_rejects_overweight_declaration(client: TestClient, post_reading) -> None:
    _harvest(client, post_reading)
    client.post(
        "/api/batches",
        json={
            "batch_id": "BT-FAT",
            "harvest_ids": ["HV-B1"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 20.0,
            "lab_test_result": "pass",
            "lab_notes": "inflated",
        },
    )
    rejected = client.post("/api/batches/BT-FAT/commit")
    assert rejected.status_code == 409
    stored = client.get("/api/batches/BT-FAT")
    assert stored.json()["status"] == "rejected"
    events = client.get("/api/oracle-events")
    assert events.status_code == 200
    assert any(item["batch_id"] == "BT-FAT" and item["status"] == "rejected" for item in events.json())
    watch = client.get("/api/clonewatch")
    assert watch.status_code == 200
    assert watch.json()["oracle_failures"] >= 1
    assert any(item["reference_id"] == "BT-FAT" for item in watch.json()["flagged_items"])


def test_batch_unknown_harvest_404(client: TestClient) -> None:
    response = client.post(
        "/api/batches",
        json={
            "batch_id": "BT-MISS",
            "harvest_ids": ["HV-NOPE"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pass",
        },
    )
    assert response.status_code == 404


def test_duplicate_batch_409(client: TestClient, post_reading) -> None:
    _harvest(client, post_reading)
    payload = {
        "batch_id": "BT-DUP",
        "harvest_ids": ["HV-B1"],
        "processing_date": "2026-09-14T15:00:00+00:00",
        "declared_weight_kg": 6.0,
        "lab_test_result": "pass",
    }
    assert client.post("/api/batches", json=payload).status_code == 201
    assert client.post("/api/batches", json=payload).status_code == 409


def test_get_missing_batch_404(client: TestClient) -> None:
    assert client.get("/api/batches/NOPE").status_code == 404


def test_update_and_delete_draft_batch(client: TestClient, post_reading) -> None:
    _harvest(client, post_reading)
    client.post(
        "/api/batches",
        json={
            "batch_id": "BT-EDIT",
            "harvest_ids": ["HV-B1"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pending",
        },
    )
    patched = client.patch("/api/batches/BT-EDIT", json={"lab_test_result": "pass"})
    assert patched.status_code == 200
    assert patched.json()["lab_test_result"] == "pass"
    assert client.delete("/api/batches/BT-EDIT").status_code == 204
    assert client.get("/api/batches/BT-EDIT").status_code == 404


def test_delete_committed_batch_409(client: TestClient, post_reading) -> None:
    _harvest(client, post_reading)
    client.post(
        "/api/batches",
        json={
            "batch_id": "BT-LOCK",
            "harvest_ids": ["HV-B1"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pass",
        },
    )
    assert client.post("/api/batches/BT-LOCK/commit").status_code == 200
    assert client.delete("/api/batches/BT-LOCK").status_code == 409
