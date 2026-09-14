from __future__ import annotations

from fastapi.testclient import TestClient

def test_insights_need_five_readings(client: TestClient) -> None:
    too_few = client.get("/api/insights/IN-WB-001")
    assert too_few.status_code == 409

    for index in range(5):
        client.post(
            "/api/sensor-readings",
            json={
                "hive_id": "IN-WB-001",
                "timestamp": f"2026-09-14T10:0{index}:00+00:00",
                "inside_temperature_c": 34.2 + index * 0.05,
                "outside_temperature_c": 31.0,
                "humidity_pct": 68.0,
                "weight_kg": 42.8 + index * 0.01,
                "source": "simulated",
            },
        )
    ok = client.get("/api/insights/IN-WB-001")
    assert ok.status_code == 200, ok.text
    body = ok.json()
    assert body["health"]["status"] in {"healthy", "stressed", "needs-inspection"}
    assert body["health"]["model_name"] == "RandomForestClassifier"
    assert "MSPB" in body["health"]["trained_on"]
    assert "Synthetic" not in body["health"]["trained_on"]
    assert body["forecast"]["predicted_weight_kg"] > 0
    assert body["forecast"]["model_name"] == "LinearRegression"
    assert body["forecast"]["predicted_honey_kg"] is None or body["forecast"]["predicted_honey_kg"] >= 0


def test_insights_unknown_hive_404(client: TestClient) -> None:
    assert client.get("/api/insights/NOPE-999").status_code == 404


def test_create_hive_conflict_409(client: TestClient) -> None:
    response = client.post(
        "/api/hives",
        json={
            "hive_id": "IN-WB-001",
            "name": "Duplicate",
            "country": "India",
            "region": "West Bengal",
            "bee_species": "Apis cerana",
            "climate_zone": "humid_subtropical",
            "data_source": "manual",
            "source_reference": "test",
            "active": True,
        },
    )
    assert response.status_code == 409
