from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.batch import BatchRecord
from backend.models.harvest import HarvestRecord
from backend.schemas.batch import BatchCreate, BatchOut, BatchUpdate, OracleDecisionOut
from backend.schemas.harvest import HarvestOut
from backend.services.ledger_service import ledger_service
from backend.services.oracle_service import evaluate_weight, log_decision


def _harvest_out(record: HarvestRecord) -> HarvestOut:
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


def _to_out(record: BatchRecord) -> BatchOut:
    return BatchOut(
        batch_id=record.batch_id,
        processing_date=record.processing_date,
        declared_weight_kg=record.declared_weight_kg,
        lab_test_result=record.lab_test_result,
        lab_notes=record.lab_notes,
        status=record.status,
        oracle_status=record.oracle_status,
        oracle_reason=record.oracle_reason,
        harvests=[_harvest_out(item) for item in record.harvests],
    )


def _load_batch(session: Session, batch_id: str) -> BatchRecord:
    record = session.scalars(
        select(BatchRecord)
        .options(selectinload(BatchRecord.harvests))
        .where(BatchRecord.batch_id == batch_id)
    ).first()
    if record is None:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' does not exist.")
    return record


def _load_harvests(session: Session, harvest_ids: list[str]) -> list[HarvestRecord]:
    unique_ids = list(dict.fromkeys(harvest_ids))
    rows = session.scalars(
        select(HarvestRecord).where(HarvestRecord.harvest_id.in_(unique_ids))
    ).all()
    found = {row.harvest_id: row for row in rows}
    missing = [item for item in unique_ids if item not in found]
    if missing:
        raise HTTPException(
            status_code=404,
            detail=f"Harvest(s) not found: {', '.join(missing)}.",
        )
    return [found[item] for item in unique_ids]


def create_batch(session: Session, payload: BatchCreate) -> BatchOut:
    if session.get(BatchRecord, payload.batch_id) is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Batch '{payload.batch_id}' already exists.",
        )
    harvests = _load_harvests(session, payload.harvest_ids)
    record = BatchRecord(
        batch_id=payload.batch_id,
        processing_date=payload.processing_date,
        declared_weight_kg=payload.declared_weight_kg,
        lab_test_result=payload.lab_test_result,
        lab_notes=payload.lab_notes,
        status="draft",
        oracle_status="pending",
        oracle_reason="",
    )
    record.harvests = harvests
    session.add(record)
    session.flush()
    return _to_out(_load_batch(session, record.batch_id))


def list_batches(session: Session) -> list[BatchOut]:
    rows = session.scalars(
        select(BatchRecord)
        .options(selectinload(BatchRecord.harvests))
        .order_by(BatchRecord.batch_id)
    ).all()
    return [_to_out(row) for row in rows]


def get_batch(session: Session, batch_id: str) -> BatchOut:
    return _to_out(_load_batch(session, batch_id))


def update_batch(session: Session, batch_id: str, payload: BatchUpdate) -> BatchOut:
    record = _load_batch(session, batch_id)
    if record.status == "committed":
        raise HTTPException(
            status_code=409,
            detail=f"Batch '{batch_id}' is committed and cannot be edited.",
        )
    if payload.declared_weight_kg is not None:
        record.declared_weight_kg = payload.declared_weight_kg
    if payload.lab_test_result is not None:
        record.lab_test_result = payload.lab_test_result
    if payload.lab_notes is not None:
        record.lab_notes = payload.lab_notes
    if payload.harvest_ids is not None:
        record.harvests = _load_harvests(session, payload.harvest_ids)
    record.oracle_status = "pending"
    record.oracle_reason = ""
    record.status = "draft"
    session.flush()
    return _to_out(_load_batch(session, batch_id))


def delete_batch(session: Session, batch_id: str) -> None:
    record = _load_batch(session, batch_id)
    if record.status == "committed":
        raise HTTPException(
            status_code=409,
            detail=f"Batch '{batch_id}' is committed and cannot be deleted.",
        )
    session.delete(record)
    session.flush()


def commit_batch(session: Session, batch_id: str) -> BatchOut:
    record = _load_batch(session, batch_id)
    if record.status == "committed":
        raise HTTPException(
            status_code=409,
            detail=f"Batch '{batch_id}' is already committed.",
        )

    # Lab inspector writes to lab_test_result via /api/lab/results.
    # Existing clients that already set lab_test_result="pass" on create
    # keep working. A recorded fail blocks commit.
    if record.lab_test_result == "fail":
        raise HTTPException(
            status_code=409,
            detail="Lab result is fail. The batch cannot be committed until it passes inspection.",
        )
    if record.lab_test_result != "pass":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Batch '{batch_id}' is waiting for lab inspection "
                f"(current result: '{record.lab_test_result}'). "
                "Record a pass on the Lab desk before running the oracle."
            ),
        )

    result = evaluate_weight(record.declared_weight_kg, list(record.harvests))
    log_decision(session, record.batch_id, result)
    record.oracle_status = result.status
    record.oracle_reason = result.reason

    if not result.passed:
        record.status = "rejected"
        session.flush()
        raise HTTPException(status_code=409, detail=result.reason)

    ledger_service.commit_batch(session, record)
    record.status = "committed"
    session.flush()
    return _to_out(_load_batch(session, batch_id))


def list_oracle_events(session: Session) -> list[OracleDecisionOut]:
    from backend.models.oracle import OracleEventRecord

    rows = session.scalars(
        select(OracleEventRecord).order_by(OracleEventRecord.decided_at.desc())
    ).all()
    return [
        OracleDecisionOut(
            batch_id=row.batch_id,
            status=row.status,
            reason=row.reason,
            declared_weight_kg=row.declared_weight_kg,
            sensor_logged_sum_kg=row.sensor_logged_sum_kg,
            tolerance_pct=row.tolerance_pct,
            decided_at=row.decided_at,
        )
        for row in rows
    ]
