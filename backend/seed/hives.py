"""Extra cluster hives and a short synthetic telemetry history.

Ranges are documented here. RNG seed 20260914 makes a reset replay the
same day-one picture. Live simulator ticks after this are new events.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.assignment import HiveAssignmentRecord
from backend.models.beekeeper import BeekeeperRecord
from backend.models.hive import HiveRecord
from backend.models.sensor import SensorReadingRecord
from backend.schemas.telemetry import SensorReading
from backend.services.sensor_service import store_reading

SEED_RNG = 20260914
READINGS_PER_HIVE = 10

EXTRA_HIVES: list[dict[str, str | bool]] = [
    {
        "hive_id": "IN-WB-002",
        "name": "Nadia Cluster Hive",
        "country": "India",
        "region": "West Bengal",
        "bee_species": "Apis cerana",
        "climate_zone": "humid_subtropical",
        "data_source": "simulated",
        "source_reference": "HoneyChain one-time demo seed",
        "active": True,
    },
    {
        "hive_id": "IN-WB-003",
        "name": "Murshidabad Cluster Hive",
        "country": "India",
        "region": "West Bengal",
        "bee_species": "Apis cerana",
        "climate_zone": "humid_subtropical",
        "data_source": "simulated",
        "source_reference": "HoneyChain one-time demo seed",
        "active": True,
    },
    {
        "hive_id": "IN-KA-001",
        "name": "Kodagu Demonstration Hive",
        "country": "India",
        "region": "Karnataka",
        "bee_species": "Apis cerana",
        "climate_zone": "tropical",
        "data_source": "simulated",
        "source_reference": "HoneyChain one-time demo seed",
        "active": True,
    },
]

EXTRA_KEEPERS = [
    {
        "beekeeper_id": "BK-KA-01",
        "name": "Priya Hegde",
        "cluster": "Kodagu Cooperative",
        "region": "Karnataka",
    }
]

EXTRA_ASSIGNMENTS = {
    "IN-WB-002": "BK-WB-01",
    "IN-WB-003": "BK-WB-01",
    "IN-KA-001": "BK-KA-01",
}

# Climate-plausible starting points and walk ranges for the seed window.
PROFILES: dict[str, dict[str, tuple[float, float, float]]] = {
    # field: (start, low, high)
    "IN-WB-001": {
        "inside_temperature_c": (34.2, 31.0, 37.0),
        "outside_temperature_c": (31.0, 24.0, 36.0),
        "humidity_pct": (68.0, 50.0, 85.0),
        "weight_kg": (42.8, 38.0, 50.0),
    },
    "IN-WB-002": {
        "inside_temperature_c": (34.6, 31.0, 37.0),
        "outside_temperature_c": (30.4, 24.0, 36.0),
        "humidity_pct": (71.0, 50.0, 88.0),
        "weight_kg": (41.2, 37.0, 49.0),
    },
    "IN-WB-003": {
        "inside_temperature_c": (33.8, 31.0, 37.0),
        "outside_temperature_c": (29.8, 24.0, 36.0),
        "humidity_pct": (74.0, 52.0, 90.0),
        "weight_kg": (43.5, 38.0, 51.0),
    },
    "DE-001": {
        "inside_temperature_c": (33.4, 30.0, 36.0),
        "outside_temperature_c": (16.5, 8.0, 26.0),
        "humidity_pct": (58.0, 42.0, 80.0),
        "weight_kg": (44.1, 38.0, 52.0),
    },
    "IN-KA-001": {
        "inside_temperature_c": (34.0, 31.0, 37.0),
        "outside_temperature_c": (26.0, 18.0, 32.0),
        "humidity_pct": (64.0, 45.0, 85.0),
        "weight_kg": (40.6, 36.0, 48.0),
    },
}


def seed_extra_hives(session: Session) -> None:
    for row in EXTRA_HIVES:
        if session.get(HiveRecord, row["hive_id"]) is None:
            session.add(HiveRecord(**row))
    for row in EXTRA_KEEPERS:
        if session.get(BeekeeperRecord, row["beekeeper_id"]) is None:
            session.add(BeekeeperRecord(**row))
    session.flush()
    for hive_id, beekeeper_id in EXTRA_ASSIGNMENTS.items():
        if session.get(HiveAssignmentRecord, hive_id) is None:
            session.add(HiveAssignmentRecord(hive_id=hive_id, beekeeper_id=beekeeper_id))
    session.flush()


def seed_telemetry_history(session: Session) -> None:
    origin = datetime(2026, 9, 13, 6, 0, tzinfo=timezone.utc)
    for hive_id, fields in PROFILES.items():
        rng = random.Random(SEED_RNG + sum(ord(ch) for ch in hive_id))
        state = {key: start for key, (start, _lo, _hi) in fields.items()}
        for step in range(READINGS_PER_HIVE):
            stamp = origin + timedelta(minutes=18 * step, seconds=sum(ord(ch) for ch in hive_id) % 17)
            existing = session.scalars(
                select(SensorReadingRecord)
                .where(SensorReadingRecord.hive_id == hive_id)
                .where(SensorReadingRecord.timestamp == stamp)
            ).first()
            if existing is not None:
                continue
            for key, (_start, low, high) in fields.items():
                step_sigma = 0.08 if "temp" in key else 0.25 if "humidity" in key else 0.02
                state[key] = min(high, max(low, state[key] + rng.gauss(0, step_sigma)))
            store_reading(
                session,
                SensorReading(
                    hive_id=hive_id,
                    timestamp=stamp,
                    inside_temperature_c=round(state["inside_temperature_c"], 2),
                    outside_temperature_c=round(state["outside_temperature_c"], 2),
                    humidity_pct=round(state["humidity_pct"], 2),
                    weight_kg=round(state["weight_kg"], 3),
                    source="simulated",
                ),
            )
