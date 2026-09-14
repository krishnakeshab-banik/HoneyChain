from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_beekeepers(client: TestClient) -> None:
    response = client.get("/api/beekeepers")
    assert response.status_code == 200
    ids = [item["beekeeper_id"] for item in response.json()]
    assert "BK-WB-01" in ids
    assert "BK-DE-01" in ids


def test_create_harvest_happy_path(client: TestClient, post_reading) -> None:
    post_reading()
    response = client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-001",
            "hive_id": "IN-WB-001",
            "beekeeper_id": "BK-WB-01",
            "harvested_at": "2026-09-14T12:00:00+00:00",
            "raw_weight_kg": 6.4,
            "moisture_pct": 17.1,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["sensor_logged_weight_kg"] == 6.4
    assert body["hive_weight_at_harvest_kg"] == 42.8


def test_create_harvest_unknown_hive_404(client: TestClient) -> None:
    response = client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-404",
            "hive_id": "NOPE-999",
            "beekeeper_id": "BK-WB-01",
            "harvested_at": "2026-09-14T12:00:00+00:00",
            "raw_weight_kg": 6.4,
            "moisture_pct": 17.1,
        },
    )
    assert response.status_code == 404


def test_create_harvest_without_sensors_409(client: TestClient) -> None:
    response = client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-NOSENSOR",
            "hive_id": "IN-WB-001",
            "beekeeper_id": "BK-WB-01",
            "harvested_at": "2026-09-14T12:00:00+00:00",
            "raw_weight_kg": 6.4,
            "moisture_pct": 17.1,
        },
    )
    assert response.status_code == 409


def test_create_harvest_exceeds_hive_weight_409(client: TestClient, post_reading) -> None:
    post_reading(weight_kg=10.0)
    response = client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-HEAVY",
            "hive_id": "IN-WB-001",
            "beekeeper_id": "BK-WB-01",
            "harvested_at": "2026-09-14T12:00:00+00:00",
            "raw_weight_kg": 25.0,
            "moisture_pct": 17.1,
        },
    )
    assert response.status_code == 409


def test_duplicate_harvest_409(client: TestClient, post_reading) -> None:
    post_reading()
    payload = {
        "harvest_id": "HV-DUP",
        "hive_id": "IN-WB-001",
        "beekeeper_id": "BK-WB-01",
        "harvested_at": "2026-09-14T12:00:00+00:00",
        "raw_weight_kg": 5.0,
        "moisture_pct": 16.0,
    }
    assert client.post("/api/harvests", json=payload).status_code == 201
    assert client.post("/api/harvests", json=payload).status_code == 409


def test_get_missing_harvest_404(client: TestClient) -> None:
    assert client.get("/api/harvests/NOPE").status_code == 404


def test_update_and_delete_harvest(client: TestClient, post_reading) -> None:
    post_reading()
    client.post(
        "/api/harvests",
        json={
            "harvest_id": "HV-EDIT",
            "hive_id": "IN-WB-001",
            "beekeeper_id": "BK-WB-01",
            "harvested_at": "2026-09-14T12:00:00+00:00",
            "raw_weight_kg": 5.0,
            "moisture_pct": 16.0,
        },
    )
    patched = client.patch("/api/harvests/HV-EDIT", json={"moisture_pct": 15.2})
    assert patched.status_code == 200
    assert patched.json()["moisture_pct"] == 15.2
    deleted = client.delete("/api/harvests/HV-EDIT")
    assert deleted.status_code == 204
    assert client.get("/api/harvests/HV-EDIT").status_code == 404
