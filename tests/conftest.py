from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("HONEYCHAIN_SKIP_DEMO_SEED", "1")

from backend.database import reset_engine
from backend.main import create_app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    url = f"sqlite:///{(tmp_path / 'honeychain-test.db').as_posix()}"
    reset_engine(url)
    application = create_app(bootstrap=True)
    with TestClient(application) as test_client:
        yield test_client


def add_reading(
    client: TestClient,
    hive_id: str = "IN-WB-001",
    weight_kg: float = 42.8,
    humidity_pct: float = 68.0,
    inside: float = 34.2,
    timestamp: str = "2026-09-14T10:00:00+00:00",
) -> None:
    response = client.post(
        "/api/sensor-readings",
        json={
            "hive_id": hive_id,
            "timestamp": timestamp,
            "inside_temperature_c": inside,
            "outside_temperature_c": 31.0,
            "humidity_pct": humidity_pct,
            "weight_kg": weight_kg,
            "source": "simulated",
        },
    )
    assert response.status_code == 201, response.text


@pytest.fixture()
def post_reading(client: TestClient):
    def _post(
        hive_id: str = "IN-WB-001",
        weight_kg: float = 42.8,
        humidity_pct: float = 68.0,
        inside: float = 34.2,
        timestamp: str = "2026-09-14T10:00:00+00:00",
    ) -> None:
        add_reading(
            client,
            hive_id=hive_id,
            weight_kg=weight_kg,
            humidity_pct=humidity_pct,
            inside=inside,
            timestamp=timestamp,
        )

    return _post
