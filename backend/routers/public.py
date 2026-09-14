from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.public import PublicImpact, PublicStats
from backend.services import public_service

router = APIRouter(prefix="/api/public", tags=["public"])


@router.get("/stats", response_model=PublicStats)
def get_stats(session: Session = Depends(get_db)) -> PublicStats:
    return public_service.stats(session)


@router.get("/impact", response_model=PublicImpact)
def get_impact(session: Session = Depends(get_db)) -> PublicImpact:
    return public_service.impact(session)


@router.get("/market")
def get_public_market(session: Session = Depends(get_db)) -> dict:
    return public_service.market_preview(session)
