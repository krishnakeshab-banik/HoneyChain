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


def _token(client: TestClient, username: str, password: str) -> str:
    return client.post("/api/auth/login", json={"username": username, "password": password}).json()["access_token"]


def test_lab_result_and_wrong_role(client: TestClient, post_reading) -> None:
    _harvest(client, post_reading)
    client.post(
        "/api/batches",
        json={
            "batch_id": "BT-LAB",
            "harvest_ids": ["HV-B1"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pending",
        },
    )
    assert client.post(
        "/api/lab/results",
        json={"batch_id": "BT-LAB", "moisture_pct": 17.1, "purity_pct": 92, "result": "pass"},
    ).status_code == 401

    beekeeper = _token(client, "beekeeper", "Beekeeper123!")
    assert client.get("/api/lab/queue", headers={"Authorization": f"Bearer {beekeeper}"}).status_code == 403

    lab = _token(client, "lab", "Lab123!")
    created = client.post(
        "/api/lab/results",
        headers={"Authorization": f"Bearer {lab}"},
        json={"batch_id": "BT-LAB", "moisture_pct": 17.1, "purity_pct": 92, "result": "pass", "notes": "ok"},
    )
    assert created.status_code == 201, created.text
    assert created.json()["inspector"] == "lab"


def test_pending_lab_blocks_commit_until_pass(client: TestClient, post_reading) -> None:
    _harvest(client, post_reading, "HV-LABP")
    client.post(
        "/api/batches",
        json={
            "batch_id": "BT-LABP",
            "harvest_ids": ["HV-LABP"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pending",
        },
    )
    blocked = client.post("/api/batches/BT-LABP/commit")
    assert blocked.status_code == 409
    assert "lab" in blocked.json()["detail"].lower()
    lab = _token(client, "lab", "Lab123!")
    queue = client.get("/api/lab/queue", headers={"Authorization": f"Bearer {lab}"})
    assert queue.status_code == 200
    assert "BT-LABP" in queue.json()["pending_batch_ids"]
    recorded = client.post(
        "/api/lab/results",
        headers={"Authorization": f"Bearer {lab}"},
        json={"batch_id": "BT-LABP", "moisture_pct": 17.1, "purity_pct": 92, "result": "pass", "notes": "ok"},
    )
    assert recorded.status_code == 201, recorded.text
    committed = client.post("/api/batches/BT-LABP/commit")
    assert committed.status_code == 200, committed.text
    assert committed.json()["lab_test_result"] == "pass"


def test_lab_fail_blocks_commit(client: TestClient, post_reading) -> None:
    _harvest(client, post_reading, "HV-LABF")
    client.post(
        "/api/batches",
        json={
            "batch_id": "BT-LABF",
            "harvest_ids": ["HV-LABF"],
            "processing_date": "2026-09-14T15:00:00+00:00",
            "declared_weight_kg": 6.0,
            "lab_test_result": "pending",
        },
    )
    lab = _token(client, "lab", "Lab123!")
    client.post(
        "/api/lab/results",
        headers={"Authorization": f"Bearer {lab}"},
        json={"batch_id": "BT-LABF", "moisture_pct": 22, "purity_pct": 70, "result": "fail"},
    )
    rejected = client.post("/api/batches/BT-LABF/commit")
    assert rejected.status_code == 409
    assert "Lab result is fail" in rejected.json()["detail"]


def test_market_role_gates_and_interest(client: TestClient) -> None:
    assert client.get("/api/market/demands").status_code == 401
    beekeeper = _token(client, "beekeeper", "Beekeeper123!")
    listed = client.get("/api/market/demands", headers={"Authorization": f"Bearer {beekeeper}"})
    assert listed.status_code == 200
    assert all(item["demand_id"] not in {"DEM-WB-01", "DEM-MH-01"} for item in listed.json())

    forbidden = client.post(
        "/api/market/demands",
        headers={"Authorization": f"Bearer {beekeeper}"},
        json={
            "demand_id": "DEM-NOPE",
            "buyer_name": "X",
            "region": "West Bengal",
            "quantity_kg": 10,
            "price_min_inr": 1,
            "price_max_inr": 2,
        },
    )
    assert forbidden.status_code == 403

    admin = _token(client, "admin", "Admin123!")
    created = client.post(
        "/api/market/demands",
        headers={"Authorization": f"Bearer {admin}"},
        json={
            "demand_id": "DEM-NEW",
            "buyer_name": "Pune Buyer",
            "region": "Maharashtra",
            "quantity_kg": 50,
            "price_min_inr": 250,
            "price_max_inr": 300,
            "notes": "litchi",
        },
    )
    assert created.status_code == 201, created.text

    interest = client.post(
        "/api/market/demands/DEM-NEW/interest",
        headers={"Authorization": f"Bearer {beekeeper}"},
        json={"offered_kg": 12},
    )
    assert interest.status_code == 201
    prices = client.get("/api/market/prices", headers={"Authorization": f"Bearer {beekeeper}"})
    assert prices.status_code == 200
    assert all(item["batch_id"] != "BT-SEED-PLACEHOLDER" for item in prices.json())
    assert all(not str(item["sale_id"]).startswith("SALE-SEED") for item in prices.json())


def test_public_stats_are_live(client: TestClient) -> None:
    stats = client.get("/api/public/stats")
    assert stats.status_code == 200
    body = stats.json()
    assert body["hives_connected"] >= 2
    assert "batches_verified" in body
    assert "flagged_attempts" in body
