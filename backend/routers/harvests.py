from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_optional_user, require_hive_access
from backend.models.user import UserRecord
from backend.schemas.harvest import BeekeeperOut, HarvestCreate, HarvestOut, HarvestUpdate
from backend.services import harvest_service, me_service

router = APIRouter(prefix="/api", tags=["harvests"])


@router.get("/beekeepers", response_model=list[BeekeeperOut])
def get_beekeepers(session: Session = Depends(get_db)) -> list[BeekeeperOut]:
    return harvest_service.list_beekeepers(session)


@router.get("/harvests", response_model=list[HarvestOut])
def get_harvests(
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> list[HarvestOut]:
    rows = harvest_service.list_harvests(session)
    if user is None or user.role == "admin":
        return rows
    allowed = {item["harvest_id"] for item in me_service.harvests_for_user(session, user)}
    return [row for row in rows if row.harvest_id in allowed]


@router.post("/harvests", response_model=HarvestOut, status_code=201)
def create_harvest(
    payload: HarvestCreate,
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> HarvestOut:
    if user is not None:
        require_hive_access(payload.hive_id, user, session)
        if user.role == "beekeeper":
            if not user.beekeeper_id:
                from fastapi import HTTPException

                raise HTTPException(status_code=403, detail="Beekeeper profile is missing.")
            payload = payload.model_copy(update={"beekeeper_id": user.beekeeper_id})
    return harvest_service.create_harvest(session, payload)


@router.get("/harvests/{harvest_id}", response_model=HarvestOut)
def get_harvest(
    harvest_id: str,
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> HarvestOut:
    harvest = harvest_service.get_harvest(session, harvest_id)
    if user is not None:
        require_hive_access(harvest.hive_id, user, session)
        if user.role == "beekeeper" and harvest.beekeeper_id != user.beekeeper_id:
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="That harvest belongs to another beekeeper.")
    return harvest


@router.patch("/harvests/{harvest_id}", response_model=HarvestOut)
def update_harvest(
    harvest_id: str,
    payload: HarvestUpdate,
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> HarvestOut:
    harvest = harvest_service.get_harvest(session, harvest_id)
    if user is not None:
        require_hive_access(harvest.hive_id, user, session)
        if user.role == "beekeeper" and harvest.beekeeper_id != user.beekeeper_id:
            from fastapi import HTTPException

            raise HTTPException(status_code=403, detail="That harvest belongs to another beekeeper.")
    return harvest_service.update_harvest(session, harvest_id, payload)


@router.delete("/harvests/{harvest_id}", status_code=204)
def delete_harvest(
    harvest_id: str,
    session: Session = Depends(get_db),
) -> Response:
    harvest_service.delete_harvest(session, harvest_id)
    return Response(status_code=204)
