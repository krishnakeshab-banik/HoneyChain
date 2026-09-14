"""Give a newly registered hive enough telemetry to be usable without a local simulator."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.assignment import HiveAssignmentRecord
from backend.models.beekeeper import BeekeeperRecord
from backend.models.hive import HiveRecord
from backend.models.user import UserRecord
from backend.schemas.telemetry import Hive, SensorReading
from backend.services.hive_service import get_hive, require_hive
from backend.services.sensor_service import reading_count, store_reading

STARTER_READINGS = 12


def assign_hive(session: Session, hive_id: str, beekeeper_id: str) -> None:
    require_hive(session, hive_id)
    keeper = session.get(BeekeeperRecord, beekeeper_id)
    if keeper is None:
        raise HTTPException(status_code=404, detail=f"Beekeeper '{beekeeper_id}' does not exist.")
    existing = session.get(HiveAssignmentRecord, hive_id)
    if existing is None:
        session.add(HiveAssignmentRecord(hive_id=hive_id, beekeeper_id=beekeeper_id))
    else:
        existing.beekeeper_id = beekeeper_id
    session.flush()


def seed_starter_readings(session: Session, hive_id: str, count: int = STARTER_READINGS) -> int:
    """Write a short simulated scale history if this hive has none."""
    require_hive(session, hive_id)
    existing = reading_count(session, hive_id)
    if existing >= 5:
        return existing
    hive = session.get(HiveRecord, hive_id)
    tropical = (hive.climate_zone or "").lower() in {"tropical", "humid_subtropical"} if hive else True
    inside = 34.1 if tropical else 33.4
    outside = 29.5 if tropical else 18.0
    humidity = 66.0 if tropical else 55.0
    weight = 45.4
    origin = datetime.now(timezone.utc) - timedelta(hours=count)
    for step in range(count - existing):
        store_reading(
            session,
            SensorReading(
                hive_id=hive_id,
                timestamp=origin + timedelta(minutes=18 * step),
                inside_temperature_c=round(inside + 0.04 * step, 2),
                outside_temperature_c=round(outside + 0.03 * step, 2),
                humidity_pct=round(min(88.0, humidity + 0.15 * step), 2),
                weight_kg=round(weight + 0.04 * step, 3),
                source="simulated",
            ),
        )
    session.flush()
    return reading_count(session, hive_id)


def _region_code(region: str | None) -> str:
    text = (region or "India").upper()
    mapping = (
        ("WEST BENGAL", "WB"),
        ("KERALA", "KL"),
        ("KARNATAKA", "KA"),
        ("TAMIL", "TN"),
        ("ASSAM", "AS"),
        ("MAHARASHTRA", "MH"),
        ("TELANGANA", "TS"),
        ("ANDHRA", "AP"),
    )
    for needle, code in mapping:
        if needle in text:
            return code
    letters = re.sub(r"[^A-Z]", "", text)
    return (letters[:2] or "IN")


def _unique_hive_id(session: Session, user: UserRecord) -> str:
    slug = re.sub(r"[^A-Z0-9]", "", (user.username or "NEW").upper())[:6] or "NEW"
    base = f"IN-{_region_code(user.region)}-{slug}"
    if session.get(HiveRecord, base) is None:
        return base
    for index in range(2, 80):
        candidate = f"{base}-{index}"
        if session.get(HiveRecord, candidate) is None:
            return candidate
    raise HTTPException(status_code=409, detail="Could not allocate a hive id.")


def assigned_hive_ids(session: Session, beekeeper_id: str) -> list[str]:
    return list(
        session.scalars(
            select(HiveAssignmentRecord.hive_id).where(HiveAssignmentRecord.beekeeper_id == beekeeper_id)
        ).all()
    )


def provision_colony_for_beekeeper(session: Session, user: UserRecord) -> Hive | None:
    """Assign a usable hive (with starter readings) to a beekeeper who has none."""
    if user.role != "beekeeper" or not user.beekeeper_id:
        return None
    existing = assigned_hive_ids(session, user.beekeeper_id)
    if existing:
        return get_hive(session, existing[0])
    hive_id = _unique_hive_id(session, user)
    region = user.region or "India"
    session.add(
        HiveRecord(
            hive_id=hive_id,
            name=f"{user.display_name}'s hive",
            country="India",
            region=region,
            bee_species="Apis cerana",
            climate_zone="tropical",
            data_source="simulated",
            source_reference="Auto-assigned at beekeeper registration",
            active=True,
        )
    )
    session.flush()
    assign_hive(session, hive_id, user.beekeeper_id)
    seed_starter_readings(session, hive_id)
    return get_hive(session, hive_id)
