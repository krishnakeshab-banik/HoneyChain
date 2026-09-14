from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_optional_user, require_hive_access, scoped_hives
from backend.models.user import UserRecord
from backend.schemas.telemetry import Hive
from backend.services import hive_service

router = APIRouter(prefix="/api", tags=["hives"])


@router.get("/hives", response_model=list[Hive])
def get_all_hives(
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> list[Hive]:
    return scoped_hives(session, user)


@router.get("/hives/{hive_id}", response_model=Hive)
def get_one_hive(
    hive_id: str,
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> Hive:
    require_hive_access(hive_id, user, session)
    return hive_service.get_hive(session, hive_id)


@router.post("/hives", response_model=Hive, status_code=201)
def create_hive(
    payload: Hive,
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> Hive:
    if user is not None and user.role not in {"admin", "officer"}:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Only an officer or admin can register a hive.")
    return hive_service.create_hive(session, payload)
