from __future__ import annotations

from fastapi.testclient import TestClient

from backend import database
from backend.seed.story import apply_demo_story


def test_demo_seed_is_idempotent_and_creates_story(client: TestClient) -> None:
    session = database.SessionLocal()
    try:
        apply_demo_story(session)
        session.commit()
        apply_demo_story(session)
        session.commit()
    finally:
        session.close()

    hives = {item["hive_id"] for item in client.get("/api/hives").json()}
    assert {"IN-WB-001", "DE-001", "IN-WB-002", "IN-WB-003", "IN-KA-001"} <= hives
    chain = client.get("/api/ledger/chain")
    assert chain.status_code == 200
    ids = [row["batch_id"] for row in chain.json()]
    assert "BT-DEMO-01" in ids
    assert "BT-DEMO-02" in ids
    integrity = client.get("/api/ledger/integrity")
    assert integrity.json()["valid"] is True
    token = client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]
    sales = client.get("/api/market/prices", headers={"Authorization": f"Bearer {token}"})
    assert sales.status_code == 200
    assert any(row["sale_id"] == "SALE-DEMO-01" for row in sales.json())
    assert all(row["batch_id"] != "BT-SEED-PLACEHOLDER" for row in sales.json())
    history = client.get("/api/hives/IN-WB-002/sensor-readings")
    assert len(history.json()) == 10
