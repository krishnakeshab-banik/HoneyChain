from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import require_roles
from backend.models.user import UserRecord
from backend.schemas.lab import LabResultCreate, LabResultOut
from backend.services import lab_service

router = APIRouter(prefix="/api/lab", tags=["lab"])


@router.post("/results", response_model=LabResultOut, status_code=201)
def create_lab_result(
    payload: LabResultCreate,
    session: Session = Depends(get_db),
    user: UserRecord = Depends(require_roles("lab", "admin")),
) -> LabResultOut:
    return lab_service.submit_result(session, payload, user.username)


@router.get("/results", response_model=list[LabResultOut])
def get_lab_results(
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("lab", "admin", "officer")),
) -> list[LabResultOut]:
    return lab_service.list_results(session)


@router.get("/queue")
def get_lab_queue(
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("lab", "admin")),
) -> dict[str, list[str]]:
    return {"pending_batch_ids": lab_service.pending_batches(session)}
