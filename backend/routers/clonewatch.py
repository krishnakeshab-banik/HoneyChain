from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.clonewatch import CloneWatchReport
from backend.services import clonewatch_service

router = APIRouter(prefix="/api", tags=["clonewatch"])


@router.get("/clonewatch", response_model=CloneWatchReport)
def get_clonewatch(session: Session = Depends(get_db)) -> CloneWatchReport:
    return clonewatch_service.build_report(session)
