from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_optional_user, require_hive_access
from backend.models.user import UserRecord
from backend.schemas.insights import InsightsOut
from backend.services.ml_service import ml_service

router = APIRouter(prefix="/api", tags=["insights"])


@router.get("/insights/{hive_id}", response_model=InsightsOut)
def get_insights(
    hive_id: str,
    session: Session = Depends(get_db),
    user: UserRecord | None = Depends(get_optional_user),
) -> InsightsOut:
    require_hive_access(hive_id, user, session)
    language = user.language if user and user.language else "en"
    return ml_service.insights_for_hive(session, hive_id, language=language)
