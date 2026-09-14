from fastapi.testclient import TestClient


def test_admin_analytics_and_seller_report(client: TestClient) -> None:
    denied = client.get("/api/analytics/admin")
    assert denied.status_code == 401
    admin = client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]
    body = client.get("/api/analytics/admin", headers={"Authorization": f"Bearer {admin}"}).json()
    assert "pins" in body
    assert "report" in body
    assert body["hive_count"] >= 2
    keeper = client.post("/api/auth/login", json={"username": "beekeeper", "password": "Beekeeper123!"}).json()["access_token"]
    seller = client.get("/api/analytics/seller", headers={"Authorization": f"Bearer {keeper}"})
    assert seller.status_code == 200
    assert seller.json()["beekeeper_id"] == "BK-WB-01"
    assert "report" in seller.json()
