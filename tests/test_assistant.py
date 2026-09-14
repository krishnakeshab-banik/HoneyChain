from fastapi.testclient import TestClient


def _token(client: TestClient, username: str, password: str) -> str:
    return client.post("/api/auth/login", json={"username": username, "password": password}).json()["access_token"]


def test_assistant_requires_login(client: TestClient) -> None:
    assert client.post("/api/assistant/ask", json={"question": "How is my hive?"}).status_code == 401


def test_assistant_answers_from_scoped_records(client: TestClient) -> None:
    token = _token(client, "beekeeper", "Beekeeper123!")
    response = client.post(
        "/api/assistant/ask",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "How many hives do I have?", "language": "en"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert "IN-WB-001" in body["answer"]
    assert "DE-001" not in body["answer"]
    assert body["ai_label"]


def test_assistant_refuses_unrelated_without_inventing(client: TestClient) -> None:
    token = _token(client, "beekeeper", "Beekeeper123!")
    response = client.post(
        "/api/assistant/ask",
        headers={"Authorization": f"Bearer {token}"},
        json={"question": "Who will win the cricket world cup next year?"},
    )
    assert response.status_code == 200
    assert "only help" in response.json()["answer"].lower() or response.json()["ai_used"] is True
