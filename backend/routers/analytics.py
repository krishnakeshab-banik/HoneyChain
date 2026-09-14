from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import require_roles
from backend.models.user import UserRecord
from backend.schemas.analytics import AdminAnalyticsOut, SellerAnalyticsOut
from backend.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/admin", response_model=AdminAnalyticsOut)
def get_admin_analytics(
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("admin")),
) -> AdminAnalyticsOut:
    return analytics_service.admin_analytics(session)


@router.get("/seller", response_model=SellerAnalyticsOut)
def get_seller_analytics(
    session: Session = Depends(get_db),
    user: UserRecord = Depends(require_roles("beekeeper", "admin")),
) -> SellerAnalyticsOut:
    if user.role == "admin":
        raise HTTPException(status_code=409, detail="Use /api/analytics/admin for the cluster report.")
    if not user.beekeeper_id:
        raise HTTPException(status_code=403, detail="Beekeeper profile is missing.")
    return analytics_service.seller_analytics(session, user.beekeeper_id)
