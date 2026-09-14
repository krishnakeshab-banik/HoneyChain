from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.batch import BatchHarvestRecord, BatchRecord
from backend.models.beekeeper import BeekeeperRecord
from backend.models.harvest import HarvestRecord
from backend.schemas.harvest import BeekeeperOut, HarvestCreate, HarvestOut, HarvestUpdate
from backend.services.hive_service import require_hive
from backend.services.sensor_service import latest_reading


def _to_out(record: HarvestRecord) -> HarvestOut:
    return HarvestOut(
        harvest_id=record.harvest_id,
        hive_id=record.hive_id,
        beekeeper_id=record.beekeeper_id,
        harvested_at=record.harvested_at,
        raw_weight_kg=record.raw_weight_kg,
        moisture_pct=record.moisture_pct,
        hive_weight_at_harvest_kg=record.hive_weight_at_harvest_kg,
        sensor_logged_weight_kg=record.sensor_logged_weight_kg,
        inside_temperature_c_at_harvest=record.inside_temperature_c_at_harvest,
        humidity_pct_at_harvest=record.humidity_pct_at_harvest,
    )


def list_beekeepers(session: Session) -> list[BeekeeperOut]:
    rows = session.scalars(select(BeekeeperRecord).order_by(BeekeeperRecord.beekeeper_id)).all()
    return [
        BeekeeperOut(
            beekeeper_id=row.beekeeper_id,
            name=row.name,
            cluster=row.cluster,
            region=row.region,
        )
        for row in rows
    ]


def require_beekeeper(session: Session, beekeeper_id: str) -> BeekeeperRecord:
    record = session.get(BeekeeperRecord, beekeeper_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Beekeeper '{beekeeper_id}' does not exist.",
        )
    return record


def _corroborate_with_sensors(
    session: Session,
    hive_id: str,
    raw_weight_kg: float,
) -> tuple[float, float, float, float]:
    """Snapshot hive scale and treat the harvest amount as sensor-logged.

    Hive scales measure the whole colony, not extracted honey. The honest
    corroboration we can do without a pre/post harvest pair is: a live
    reading must exist, and extracted weight cannot exceed hive weight.
    The harvest amount then becomes the sensor-logged weight used by the
    oracle (summed across harvests and compared to the batch declaration).
    """

    reading = latest_reading(session, hive_id)
    if reading is None:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Hive '{hive_id}' has no sensor readings. "
                "A harvest cannot be corroborated without telemetry."
            ),
        )
    if raw_weight_kg > reading.weight_kg:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Harvest weight {raw_weight_kg} kg exceeds hive scale "
                f"reading {reading.weight_kg} kg."
            ),
        )
    return (
        reading.weight_kg,
        raw_weight_kg,
        reading.inside_temperature_c,
        reading.humidity_pct,
    )


def _linked_committed_batch(session: Session, harvest_id: str) -> BatchRecord | None:
    return session.scalars(
        select(BatchRecord)
        .join(BatchHarvestRecord, BatchHarvestRecord.batch_id == BatchRecord.batch_id)
        .where(BatchHarvestRecord.harvest_id == harvest_id)
        .where(BatchRecord.status == "committed")
    ).first()


def create_harvest(session: Session, payload: HarvestCreate) -> HarvestOut:
    if session.get(HarvestRecord, payload.harvest_id) is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Harvest '{payload.harvest_id}' already exists.",
        )
    require_hive(session, payload.hive_id)
    require_beekeeper(session, payload.beekeeper_id)
    hive_weight, sensor_logged, temp_c, humidity = _corroborate_with_sensors(
        session,
        payload.hive_id,
        payload.raw_weight_kg,
    )
    record = HarvestRecord(
        harvest_id=payload.harvest_id,
        hive_id=payload.hive_id,
        beekeeper_id=payload.beekeeper_id,
        harvested_at=payload.harvested_at,
        raw_weight_kg=payload.raw_weight_kg,
        moisture_pct=payload.moisture_pct,
        hive_weight_at_harvest_kg=hive_weight,
        sensor_logged_weight_kg=sensor_logged,
        inside_temperature_c_at_harvest=temp_c,
        humidity_pct_at_harvest=humidity,
    )
    session.add(record)
    session.flush()
    return _to_out(record)


def list_harvests(session: Session) -> list[HarvestOut]:
    rows = session.scalars(select(HarvestRecord).order_by(HarvestRecord.harvest_id)).all()
    return [_to_out(row) for row in rows]


def get_harvest(session: Session, harvest_id: str) -> HarvestOut:
    record = session.get(HarvestRecord, harvest_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Harvest '{harvest_id}' does not exist.")
    return _to_out(record)


def update_harvest(session: Session, harvest_id: str, payload: HarvestUpdate) -> HarvestOut:
    record = session.get(HarvestRecord, harvest_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Harvest '{harvest_id}' does not exist.")
    if _linked_committed_batch(session, harvest_id) is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Harvest '{harvest_id}' is locked in a committed batch.",
        )
    if payload.raw_weight_kg is not None:
        hive_weight, sensor_logged, temp_c, humidity = _corroborate_with_sensors(
            session,
            record.hive_id,
            payload.raw_weight_kg,
        )
        record.raw_weight_kg = payload.raw_weight_kg
        record.hive_weight_at_harvest_kg = hive_weight
        record.sensor_logged_weight_kg = sensor_logged
        record.inside_temperature_c_at_harvest = temp_c
        record.humidity_pct_at_harvest = humidity
    if payload.moisture_pct is not None:
        record.moisture_pct = payload.moisture_pct
    if payload.harvested_at is not None:
        record.harvested_at = payload.harvested_at
    session.flush()
    return _to_out(record)


def delete_harvest(session: Session, harvest_id: str) -> None:
    record = session.get(HarvestRecord, harvest_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Harvest '{harvest_id}' does not exist.")
    if _linked_committed_batch(session, harvest_id) is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Harvest '{harvest_id}' is locked in a committed batch.",
        )
    session.delete(record)
    session.flush()
