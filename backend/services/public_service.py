from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.batch import BatchRecord
from backend.models.hive import HiveRecord
from backend.models.scan import ScanRecord
from backend.schemas.public import ImpactPoint, PublicImpact, PublicStats
from backend.services import market_service


def stats(session: Session) -> PublicStats:
    hives = session.scalar(select(func.count()).select_from(HiveRecord)) or 0
    verified = session.scalar(
        select(func.count()).select_from(BatchRecord).where(BatchRecord.status == "committed")
    ) or 0
    flagged = session.scalar(
        select(func.count()).select_from(ScanRecord).where(ScanRecord.flagged.is_(True))
    ) or 0
    return PublicStats(
        hives_connected=int(hives),
        batches_verified=int(verified),
        flagged_attempts=int(flagged),
    )


def impact(session: Session) -> PublicImpact:
    current = stats(session)
    # Honest cumulative snapshot: we do not invent a fake history series.
    # One live point plus a zero baseline so the home chart has real endpoints.
    return PublicImpact(
        points=[
            ImpactPoint(label="Start", hives_connected=0, batches_verified=0, flagged_attempts=0),
            ImpactPoint(
                label="Now",
                hives_connected=current.hives_connected,
                batches_verified=current.batches_verified,
                flagged_attempts=current.flagged_attempts,
            ),
        ]
    )


def market_preview(session: Session) -> dict:
    return {
        "demands": market_service.list_demands(session),
        "prices": market_service.list_sales(session),
    }
