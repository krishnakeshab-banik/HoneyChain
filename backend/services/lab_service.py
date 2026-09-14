from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.batch import BatchRecord
from backend.models.lab import LabResultRecord
from backend.schemas.lab import LabResultCreate, LabResultOut


def _to_out(record: LabResultRecord) -> LabResultOut:
    return LabResultOut(
        result_id=record.result_id,
        batch_id=record.batch_id,
        moisture_pct=record.moisture_pct,
        purity_pct=record.purity_pct,
        result=record.result,
        notes=record.notes,
        inspector=record.inspector,
        recorded_at=record.recorded_at,
    )


def submit_result(session: Session, payload: LabResultCreate, inspector: str) -> LabResultOut:
    batch = session.get(BatchRecord, payload.batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail=f"Batch '{payload.batch_id}' does not exist.")
    if batch.status == "committed":
        raise HTTPException(status_code=409, detail="Committed batches cannot receive new lab results.")
    record = LabResultRecord(
        result_id=f"LAB-{uuid4().hex[:10]}",
        batch_id=payload.batch_id,
        moisture_pct=payload.moisture_pct,
        purity_pct=payload.purity_pct,
        result=payload.result,
        notes=payload.notes,
        inspector=inspector,
        recorded_at=datetime.now(timezone.utc),
    )
    session.add(record)
    batch.lab_test_result = payload.result
    batch.lab_notes = payload.notes
    session.flush()
    return _to_out(record)


def list_results(session: Session) -> list[LabResultOut]:
    rows = session.scalars(select(LabResultRecord).order_by(LabResultRecord.recorded_at.desc())).all()
    return [_to_out(row) for row in rows]


def pending_batches(session: Session) -> list[str]:
    rows = session.scalars(select(BatchRecord).where(BatchRecord.status == "draft")).all()
    return [row.batch_id for row in rows if row.lab_test_result == "pending"]
