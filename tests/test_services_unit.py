"""Service-level tests that do not start the HTTP stack."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.models.harvest import HarvestRecord
from backend.services.oracle_service import evaluate_weight


def _harvest(weight: float) -> HarvestRecord:
    return HarvestRecord(
        harvest_id="HV-U",
        hive_id="IN-WB-001",
        beekeeper_id="BK-WB-01",
        harvested_at=datetime.now(timezone.utc),
        raw_weight_kg=weight,
        moisture_pct=17.0,
        hive_weight_at_harvest_kg=42.0,
        sensor_logged_weight_kg=weight,
        inside_temperature_c_at_harvest=34.0,
        humidity_pct_at_harvest=65.0,
    )


def test_oracle_passes_within_tolerance() -> None:
    result = evaluate_weight(6.3, [_harvest(6.0)])
    assert result.passed is True
    assert result.status == "passed"


def test_oracle_fails_outside_tolerance() -> None:
    result = evaluate_weight(12.0, [_harvest(6.0)])
    assert result.passed is False
    assert result.status == "rejected"
    assert "10.0%" in result.reason


def test_oracle_fails_without_harvests() -> None:
    result = evaluate_weight(6.0, [])
    assert result.passed is False
