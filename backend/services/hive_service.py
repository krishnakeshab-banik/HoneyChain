from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.hive import HiveRecord
from backend.schemas.telemetry import Hive


def _to_schema(record: HiveRecord) -> Hive:
    return Hive(
        hive_id=record.hive_id,
        name=record.name,
        country=record.country,
        region=record.region,
        bee_species=record.bee_species,
        climate_zone=record.climate_zone,
        data_source=record.data_source,  # type: ignore[arg-type]
        source_reference=record.source_reference,
        active=record.active,
    )


def list_hives(session: Session) -> list[Hive]:
    rows = session.scalars(select(HiveRecord).order_by(HiveRecord.hive_id)).all()
    return [_to_schema(row) for row in rows]


def get_hive(session: Session, hive_id: str) -> Hive:
    record = session.get(HiveRecord, hive_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Hive '{hive_id}' does not exist.")
    return _to_schema(record)


def require_hive(session: Session, hive_id: str) -> HiveRecord:
    record = session.get(HiveRecord, hive_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Hive '{hive_id}' does not exist.")
    return record


def create_hive(
    session: Session,
    payload: Hive,
    *,
    seed_telemetry: bool = True,
    beekeeper_id: str | None = None,
) -> Hive:
    if session.get(HiveRecord, payload.hive_id) is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Hive '{payload.hive_id}' already exists.",
        )
    record = HiveRecord(**payload.model_dump())
    session.add(record)
    session.flush()
    if seed_telemetry:
        from backend.services.hive_bootstrap import seed_starter_readings

        seed_starter_readings(session, payload.hive_id)
    if beekeeper_id:
        from backend.services.hive_bootstrap import assign_hive

        assign_hive(session, payload.hive_id, beekeeper_id)
    return _to_schema(record)
