from __future__ import annotations

from fastapi.testclient import TestClient


def test_duplicate_timestamp_does_not_add_a_row(client: TestClient, post_reading) -> None:
    post_reading(timestamp="2026-09-14T10:00:00+00:00")
    post_reading(timestamp="2026-09-14T10:00:00+00:00")
    history = client.get("/api/hives/IN-WB-001/sensor-readings")
    assert history.status_code == 200
    assert len(history.json()) == 1
