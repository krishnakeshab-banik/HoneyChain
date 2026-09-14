from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_optional_user, require_hive_access
from backend.models.user import UserRecord
from backend.schemas.telemetry import SensorReading
from backend.services import sensor_service

router = APIRouter(prefix="/api", tags=["sensors"])


@router.post("/sensor-readings", status_code=201)
def create_sensor_reading(
    reading: SensorReading,
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    stored = sensor_service.store_reading(session, reading)
    return {
        "message": "Sensor reading stored successfully.",
        "reading": stored,
    }


@router.get("/hives/{hive_id}/sensor-readings")
def get_sensor_readings(
    hive_id: str,
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> list[SensorReading]:
    require_hive_access(hive_id, user, session)
    return sensor_service.list_readings(session, hive_id)


@router.get("/hives/{hive_id}/summary")
def get_hive_summary(
    hive_id: str,
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> dict[str, Any]:
    require_hive_access(hive_id, user, session)
    return sensor_service.hive_summary(session, hive_id)
