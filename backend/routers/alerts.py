from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import require_roles
from backend.models.user import UserRecord
from backend.services import alert_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class AlertCreate(BaseModel):
    hive_id: str = Field(..., min_length=3)
    message: str = Field(..., min_length=4)


@router.get("")
def get_alerts(
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("beekeeper", "officer", "admin")),
) -> list[dict[str, str]]:
    return alert_service.list_alerts(session)


@router.post("", status_code=201)
def create_alert(
    payload: AlertCreate,
    session: Session = Depends(get_db),
    user: UserRecord = Depends(require_roles("officer", "admin")),
) -> dict[str, str]:
    return alert_service.queue_whatsapp_alert(
        session,
        payload.hive_id,
        payload.message,
        user.role,
    )
