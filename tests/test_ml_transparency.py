from __future__ import annotations

from fastapi.testclient import TestClient


def test_public_model_is_held_out(client: TestClient) -> None:
    response = client.get("/api/public/model")
    assert response.status_code == 200
    body = response.json()
    assert "train_test_split" in body["split"]
    assert "MSPB" in body["provenance"]
    assert body["health_accuracy"] is not None
    assert 0 <= body["health_accuracy"] <= 1
    assert body["n_health_test"] and body["n_health_test"] >= 5


def test_admin_transparency_and_role_gate(client: TestClient) -> None:
    denied = client.get("/api/ml/transparency")
    assert denied.status_code == 401
    officer = client.post("/api/auth/login", json={"username": "officer", "password": "Officer123!"}).json()["access_token"]
    assert client.get("/api/ml/transparency", headers={"Authorization": f"Bearer {officer}"}).status_code == 403
    admin = client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]
    ok = client.get("/api/ml/transparency", headers={"Authorization": f"Bearer {admin}"})
    assert ok.status_code == 200, ok.text
    body = ok.json()
    assert body["health"]["n_test"] >= 5
    assert body["health"]["n_train"] >= body["health"]["n_test"]
    assert body["health_feature_importance"]
    names = {row["feature"] for row in body["health_feature_importance"]}
    assert "mean_temp" in names
    assert "never trained" in body["note"].lower() or "held-out" in body["note"].lower()
