from fastapi.testclient import TestClient


def test_public_model_and_market_do_not_hang(client: TestClient) -> None:
    model = client.get("/api/public/model")
    assert model.status_code == 200
    assert "health_accuracy" in model.json()
    market = client.get("/api/public/market")
    assert market.status_code == 200
    body = market.json()
    assert "demands" in body
    assert "prices" in body
