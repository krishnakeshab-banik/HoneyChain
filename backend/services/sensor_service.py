from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.sensor import SensorReadingRecord
from backend.schemas.telemetry import HiveSummary, HiveSummaryLatest, SensorReading
from backend.services.hive_service import require_hive


def store_reading(session: Session, reading: SensorReading) -> SensorReading:
    require_hive(session, reading.hive_id)
    record = SensorReadingRecord(
        hive_id=reading.hive_id,
        timestamp=reading.timestamp,
        inside_temperature_c=reading.inside_temperature_c,
        outside_temperature_c=reading.outside_temperature_c,
        humidity_pct=reading.humidity_pct,
        weight_kg=reading.weight_kg,
        source=reading.source,
    )
    session.add(record)
    session.flush()
    return reading


def list_readings(session: Session, hive_id: str) -> list[SensorReading]:
    require_hive(session, hive_id)
    rows = session.scalars(
        select(SensorReadingRecord)
        .where(SensorReadingRecord.hive_id == hive_id)
        .order_by(SensorReadingRecord.id.asc())
    ).all()
    return [
        SensorReading(
            hive_id=row.hive_id,
            timestamp=row.timestamp,
            inside_temperature_c=row.inside_temperature_c,
            outside_temperature_c=row.outside_temperature_c,
            humidity_pct=row.humidity_pct,
            weight_kg=row.weight_kg,
            source=row.source,  # type: ignore[arg-type]
        )
        for row in rows
    ]


def latest_reading(session: Session, hive_id: str) -> SensorReadingRecord | None:
    return session.scalars(
        select(SensorReadingRecord)
        .where(SensorReadingRecord.hive_id == hive_id)
        .order_by(SensorReadingRecord.id.desc())
        .limit(1)
    ).first()


def reading_count(session: Session, hive_id: str) -> int:
    count = session.scalar(
        select(func.count())
        .select_from(SensorReadingRecord)
        .where(SensorReadingRecord.hive_id == hive_id)
    )
    return int(count or 0)


def hive_summary(session: Session, hive_id: str) -> dict[str, object]:
    """Return the original summary dict shape used by the Streamlit dashboard."""

    require_hive(session, hive_id)
    count = reading_count(session, hive_id)
    latest = latest_reading(session, hive_id)
    if latest is None:
        return {
            "hive_id": hive_id,
            "reading_count": 0,
            "latest": None,
            "message": "No sensor readings available yet.",
        }
    return {
        "hive_id": hive_id,
        "reading_count": count,
        "latest": {
            "timestamp": latest.timestamp,
            "inside_temperature_c": latest.inside_temperature_c,
            "outside_temperature_c": latest.outside_temperature_c,
            "humidity_pct": latest.humidity_pct,
            "weight_kg": latest.weight_kg,
            "source": latest.source,
        },
    }


def require_enough_readings(session: Session, hive_id: str, minimum: int) -> list[SensorReading]:
    readings = list_readings(session, hive_id)
    if len(readings) < minimum:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Hive '{hive_id}' has {len(readings)} readings; "
                f"at least {minimum} are required."
            ),
        )
    return readings
