from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.deps import require_roles
from backend.models.user import UserRecord
from backend.schemas.ml import ModelTransparencyOut, PublicModelSummary
from backend.services import ml_transparency

router = APIRouter(tags=["ml"])


@router.get("/api/ml/transparency", response_model=ModelTransparencyOut)
def get_transparency(_user: UserRecord = Depends(require_roles("admin"))) -> ModelTransparencyOut:
    return ml_transparency.transparency()


@router.get("/api/public/model", response_model=PublicModelSummary)
def get_public_model() -> PublicModelSummary:
    return ml_transparency.public_summary()
