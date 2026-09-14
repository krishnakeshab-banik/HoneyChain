from fastapi.testclient import TestClient


def test_login_happy_path(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"username": "beekeeper", "password": "Beekeeper123!"})
    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "beekeeper"
    assert body["access_token"]


def test_login_wrong_password_401(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"username": "beekeeper", "password": "nope"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect password."


def test_login_unknown_user_401(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"username": "nobody", "password": "nope"})
    assert response.status_code == 401
    assert "No account found" in response.json()["detail"]


def test_forgot_and_reset_password(client: TestClient) -> None:
    missing = client.post("/api/auth/forgot-password", json={"username": "nobody"})
    assert missing.status_code == 401
    issued = client.post("/api/auth/forgot-password", json={"username": "beekeeper"})
    assert issued.status_code == 200
    code = issued.json()["reset_code"]
    reset = client.post(
        "/api/auth/reset-password",
        json={"username": "beekeeper", "code": code, "password": "Beekeeper456!"},
    )
    assert reset.status_code == 200
    assert client.post("/api/auth/login", json={"username": "beekeeper", "password": "Beekeeper123!"}).status_code == 401
    assert client.post("/api/auth/login", json={"username": "beekeeper", "password": "Beekeeper456!"}).status_code == 200


def test_me_requires_token_401(client: TestClient) -> None:
    assert client.get("/api/auth/me").status_code == 401


def test_me_with_token(client: TestClient) -> None:
    token = client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_beekeeper_hives_are_scoped(client: TestClient) -> None:
    token = client.post("/api/auth/login", json={"username": "beekeeper", "password": "Beekeeper123!"}).json()["access_token"]
    response = client.get("/api/auth/me/hives", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert [item["hive_id"] for item in response.json()] == ["IN-WB-001"]


def test_lab_rejected_for_beekeeper_403(client: TestClient) -> None:
    token = client.post("/api/auth/login", json={"username": "beekeeper", "password": "Beekeeper123!"}).json()["access_token"]
    response = client.post(
        "/api/lab/results",
        headers={"Authorization": f"Bearer {token}"},
        json={"batch_id": "BT-X", "moisture_pct": 17, "purity_pct": 90, "result": "pass"},
    )
    assert response.status_code == 403


def test_unauthenticated_public_routes_still_work(client: TestClient) -> None:
    assert client.get("/api/hives").status_code == 200
    assert client.get("/api/public/stats").status_code == 200
    assert client.get("/health").status_code == 200


def test_refresh_issues_new_access_token(client: TestClient) -> None:
    login = client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"})
    assert login.status_code == 200
    refresh = login.json()["refresh_token"]
    rotated = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert rotated.status_code == 200
    assert rotated.json()["access_token"]
    reused = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert reused.status_code == 401


def test_beekeeper_cannot_read_other_hive_with_token(client: TestClient) -> None:
    token = client.post("/api/auth/login", json={"username": "beekeeper", "password": "Beekeeper123!"}).json()[
        "access_token"
    ]
    denied = client.get("/api/hives/DE-001", headers={"Authorization": f"Bearer {token}"})
    assert denied.status_code == 403
    allowed = client.get("/api/hives/IN-WB-001", headers={"Authorization": f"Bearer {token}"})
    assert allowed.status_code == 200


def test_admin_creates_officer_beekeeper_cannot(client: TestClient) -> None:
    beekeeper = client.post("/api/auth/login", json={"username": "beekeeper", "password": "Beekeeper123!"}).json()[
        "access_token"
    ]
    assert (
        client.post(
            "/api/admin/users",
            headers={"Authorization": f"Bearer {beekeeper}"},
            json={
                "username": "newofficer",
                "password": "Officer123!",
                "display_name": "New Officer",
                "role": "officer",
            },
        ).status_code
        == 403
    )
    admin = client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]
    created = client.post(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin}"},
        json={
            "username": "newofficer",
            "password": "Officer123!",
            "display_name": "New Officer",
            "role": "officer",
            "region": "Kerala",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["role"] == "officer"


def test_register_ignores_role_field(client: TestClient) -> None:
    created = client.post(
        "/api/auth/register",
        json={
            "username": "sneaky",
            "password": "Sneaky123!",
            "display_name": "Sneaky",
            "region": "Assam",
            "role": "admin",
        },
    )
    assert created.status_code == 201
    assert created.json()["role"] == "beekeeper"


def test_register_beekeeper_then_me(client: TestClient) -> None:
    created = client.post(
        "/api/auth/register",
        json={
            "username": "newkeeper",
            "password": "NewKeeper1!",
            "display_name": "New Keeper",
            "region": "Karnataka",
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["role"] == "beekeeper"
    token = created.json()["access_token"]
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["region"] == "Karnataka"
