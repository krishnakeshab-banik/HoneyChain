from __future__ import annotations

from fastapi.testclient import TestClient

from backend.services.ledger_service import compute_block_hash


def test_compute_block_hash_is_sha256() -> None:
    digest = compute_block_hash('{"a":1}')
    assert len(digest) == 64
    assert digest == compute_block_hash('{"a":1}')
    assert digest != compute_block_hash('{"a":2}')


def _commit_ok(client: TestClient, post_reading, batch_id: str = "BT-LED") -> None:
    post_reading()
    client.post(
        "/api/harvests",
        json={
            "harvest_id": f"HV-{batch_id}",
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
            "batch_id": batch_id,
            "harvest_ids": [f"HV-{batch_id}"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pass",
        },
    )
    committed = client.post(f"/api/batches/{batch_id}/commit")
    assert committed.status_code == 200, committed.text


def test_chain_and_integrity_after_commit(client: TestClient, post_reading) -> None:
    empty = client.get("/api/ledger/integrity")
    assert empty.status_code == 200
    assert empty.json()["valid"] is True
    assert empty.json()["checked_blocks"] == 0

    _commit_ok(client, post_reading)
    chain = client.get("/api/ledger/chain")
    assert chain.status_code == 200
    assert len(chain.json()) == 1
    custody = client.get("/api/ledger/batches/BT-LED")
    assert custody.status_code == 200
    integrity = client.get("/api/ledger/integrity")
    assert integrity.json()["valid"] is True
    assert integrity.json()["checked_blocks"] == 1


def test_custody_missing_batch_404(client: TestClient) -> None:
    assert client.get("/api/ledger/batches/NOPE").status_code == 404


def test_double_commit_409(client: TestClient, post_reading) -> None:
    _commit_ok(client, post_reading, "BT-ONCE")
    again = client.post("/api/batches/BT-ONCE/commit")
    assert again.status_code == 409
