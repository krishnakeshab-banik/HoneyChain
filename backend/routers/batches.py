from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.batch import BatchCreate, BatchOut, BatchUpdate, OracleDecisionOut
from backend.services import batch_service

router = APIRouter(prefix="/api", tags=["batches"])


@router.get("/batches", response_model=list[BatchOut])
def get_batches(session: Session = Depends(get_db)) -> list[BatchOut]:
    return batch_service.list_batches(session)


@router.post("/batches", response_model=BatchOut, status_code=201)
def create_batch(payload: BatchCreate, session: Session = Depends(get_db)) -> BatchOut:
    return batch_service.create_batch(session, payload)


@router.get("/batches/{batch_id}", response_model=BatchOut)
def get_batch(batch_id: str, session: Session = Depends(get_db)) -> BatchOut:
    return batch_service.get_batch(session, batch_id)


@router.patch("/batches/{batch_id}", response_model=BatchOut)
def update_batch(
    batch_id: str,
    payload: BatchUpdate,
    session: Session = Depends(get_db),
) -> BatchOut:
    return batch_service.update_batch(session, batch_id, payload)


@router.delete("/batches/{batch_id}", status_code=204)
def delete_batch(batch_id: str, session: Session = Depends(get_db)) -> Response:
    batch_service.delete_batch(session, batch_id)
    return Response(status_code=204)


@router.post("/batches/{batch_id}/commit", response_model=BatchOut)
def commit_batch(batch_id: str, session: Session = Depends(get_db)) -> BatchOut:
    return batch_service.commit_batch(session, batch_id)


@router.get("/oracle-events", response_model=list[OracleDecisionOut])
def get_oracle_events(session: Session = Depends(get_db)) -> list[OracleDecisionOut]:
    return batch_service.list_oracle_events(session)
