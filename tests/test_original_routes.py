"""Happy and failure paths for the six original routes, now on SQLite."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_root_running(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["project"] == "HoneyChain"
    assert body["status"] == "running"
    assert body["version"] == "0.1.0"


def test_health_healthy(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_get_hive_by_id_and_404(client: TestClient) -> None:
    ok = client.get("/api/hives/IN-WB-001")
    assert ok.status_code == 200
    assert ok.json()["name"] == "West Bengal Demo Hive"
    assert client.get("/api/hives/NOPE-999").status_code == 404


def test_create_hive_happy_path(client: TestClient) -> None:
    response = client.post(
        "/api/hives",
        json={
            "hive_id": "IN-KL-002",
            "name": "Kerala Test Hive",
            "country": "India",
            "region": "Kerala",
            "bee_species": "Apis cerana",
            "climate_zone": "tropical",
            "data_source": "manual",
            "source_reference": "operator entry",
            "active": True,
        },
    )
    assert response.status_code == 201
    assert response.json()["hive_id"] == "IN-KL-002"


def test_list_hives_includes_both_seeded_ids(client: TestClient) -> None:
    response = client.get("/api/hives")
    assert response.status_code == 200
    ids = [item["hive_id"] for item in response.json()]
    assert ids == ["DE-001", "IN-WB-001"]
    de_hive = next(item for item in response.json() if item["hive_id"] == "DE-001")
    # DE-001 is simulated and will be fed by the multi-hive simulator.
    assert de_hive["data_source"] == "simulated"


def test_post_reading_success(client: TestClient, post_reading) -> None:
    post_reading()
    history = client.get("/api/hives/IN-WB-001/sensor-readings")
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["weight_kg"] == 42.8


def test_post_reading_unknown_hive_404(client: TestClient) -> None:
    response = client.post(
        "/api/sensor-readings",
        json={
            "hive_id": "NOPE-999",
            "timestamp": "2026-09-14T10:00:00+00:00",
            "inside_temperature_c": 34.2,
            "outside_temperature_c": 31.0,
            "humidity_pct": 68.0,
            "weight_kg": 42.8,
            "source": "simulated",
        },
    )
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]


def test_post_reading_invalid_humidity_422(client: TestClient) -> None:
    response = client.post(
        "/api/sensor-readings",
        json={
            "hive_id": "IN-WB-001",
            "timestamp": "2026-09-14T10:00:00+00:00",
            "inside_temperature_c": 34.2,
            "outside_temperature_c": 31.0,
            "humidity_pct": 140,
            "weight_kg": 42.8,
            "source": "simulated",
        },
    )
    assert response.status_code == 422


def test_summary_empty_then_latest(client: TestClient, post_reading) -> None:
    empty = client.get("/api/hives/IN-WB-001/summary")
    assert empty.status_code == 200
    assert empty.json()["reading_count"] == 0
    assert empty.json()["latest"] is None

    post_reading(weight_kg=43.1)
    filled = client.get("/api/hives/IN-WB-001/summary")
    assert filled.status_code == 200
    assert filled.json()["reading_count"] == 1
    assert filled.json()["latest"]["weight_kg"] == 43.1


def test_history_unknown_hive_404(client: TestClient) -> None:
    response = client.get("/api/hives/MISSING/sensor-readings")
    assert response.status_code == 404


def test_summary_unknown_hive_404(client: TestClient) -> None:
    response = client.get("/api/hives/MISSING/summary")
    assert response.status_code == 404


def test_readings_survive_new_client_same_file(tmp_path, monkeypatch) -> None:
    """A second app instance on the same SQLite file still sees readings."""

    from backend.database import reset_engine
    from backend.main import create_app
    from fastapi.testclient import TestClient

    url = f"sqlite:///{(tmp_path / 'persist.db').as_posix()}"
    reset_engine(url)
    first = TestClient(create_app(bootstrap=True))
    posted = first.post(
        "/api/sensor-readings",
        json={
            "hive_id": "IN-WB-001",
            "timestamp": "2026-09-14T10:00:00+00:00",
            "inside_temperature_c": 34.2,
            "outside_temperature_c": 31.0,
            "humidity_pct": 68.0,
            "weight_kg": 42.8,
            "source": "simulated",
        },
    )
    assert posted.status_code == 201
    first.close()

    reset_engine(url)
    second = TestClient(create_app(bootstrap=True))
    history = second.get("/api/hives/IN-WB-001/sensor-readings")
    assert history.status_code == 200
    assert len(history.json()) == 1
    second.close()
