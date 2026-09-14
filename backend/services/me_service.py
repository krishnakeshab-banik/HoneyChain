from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.assignment import HiveAssignmentRecord
from backend.models.batch import BatchHarvestRecord, BatchRecord
from backend.models.beekeeper import BeekeeperRecord
from backend.models.harvest import HarvestRecord
from backend.models.user import UserRecord
from backend.schemas.telemetry import Hive
from backend.services.hive_service import get_hive, list_hives


def hives_for_user(session: Session, user: UserRecord) -> list[Hive]:
    if user.role in {"admin", "lab"}:
        return list_hives(session)
    if user.role == "officer":
        all_hives = list_hives(session)
        return [hive for hive in all_hives if user.region and hive.region == user.region]
    if user.role == "beekeeper" and user.beekeeper_id:
        hive_ids = session.scalars(
            select(HiveAssignmentRecord.hive_id).where(
                HiveAssignmentRecord.beekeeper_id == user.beekeeper_id
            )
        ).all()
        if not hive_ids:
            from backend.services.hive_bootstrap import provision_colony_for_beekeeper

            hive = provision_colony_for_beekeeper(session, user)
            return [hive] if hive else []
        return [get_hive(session, hive_id) for hive_id in hive_ids]
    return []


def assert_hive_access(session: Session, user: UserRecord, hive_id: str) -> None:
    allowed = {hive.hive_id for hive in hives_for_user(session, user)}
    if hive_id not in allowed:
        raise HTTPException(
            status_code=403,
            detail=f"Role '{user.role}' cannot access hive '{hive_id}'.",
        )


def _harvest_status(session: Session, harvest_id: str) -> tuple[str, str]:
    rows = session.scalars(
        select(BatchRecord)
        .join(BatchHarvestRecord, BatchHarvestRecord.batch_id == BatchRecord.batch_id)
        .where(BatchHarvestRecord.harvest_id == harvest_id)
    ).all()
    if not rows:
        return "pending", ""
    rejected = next((row for row in rows if row.oracle_status == "rejected"), None)
    if rejected is not None:
        return "rejected", rejected.oracle_reason or "Oracle rejected this batch."
    if any(row.status == "committed" or row.status == "draft" for row in rows):
        return "batched", ""
    return "pending", ""


def harvests_for_user(session: Session, user: UserRecord) -> list[dict]:
    rows = session.scalars(select(HarvestRecord).order_by(HarvestRecord.harvest_id)).all()
    allowed_hives = {hive.hive_id for hive in hives_for_user(session, user)}
    out = []
    for row in rows:
        if user.role == "beekeeper" and row.beekeeper_id != user.beekeeper_id:
            continue
        if user.role == "officer" and row.hive_id not in allowed_hives:
            continue
        status, reason = _harvest_status(session, row.harvest_id)
        out.append(
            {
                "harvest_id": row.harvest_id,
                "hive_id": row.hive_id,
                "beekeeper_id": row.beekeeper_id,
                "harvested_at": row.harvested_at,
                "raw_weight_kg": row.raw_weight_kg,
                "moisture_pct": row.moisture_pct,
                "sensor_logged_weight_kg": row.sensor_logged_weight_kg,
                "status": status,
                "status_reason": reason,
            }
        )
    return out


def cluster_overview(session: Session, user: UserRecord) -> dict:
    hives = hives_for_user(session, user)
    keepers = session.scalars(select(BeekeeperRecord).order_by(BeekeeperRecord.beekeeper_id)).all()
    if user.role == "officer" and user.region:
        keepers = [row for row in keepers if row.region == user.region]
    return {
        "region": user.region,
        "cluster": user.cluster,
        "hives": hives,
        "beekeepers": [
            {
                "beekeeper_id": row.beekeeper_id,
                "name": row.name,
                "cluster": row.cluster,
                "region": row.region,
            }
            for row in keepers
        ],
        "harvests": harvests_for_user(session, user),
    }
