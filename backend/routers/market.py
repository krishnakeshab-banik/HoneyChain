from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import require_roles
from backend.models.user import UserRecord
from backend.schemas.market import DemandCreate, DemandOut, DemandUpdate, InterestCreate, InterestOut, SaleCreate, SaleOut
from backend.services import market_service

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/demands", response_model=list[DemandOut])
def get_demands(
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("beekeeper", "officer", "admin")),
) -> list[DemandOut]:
    return market_service.list_demands(session)


@router.post("/demands", response_model=DemandOut, status_code=201)
def post_demand(
    payload: DemandCreate,
    session: Session = Depends(get_db),
    user: UserRecord = Depends(require_roles("officer", "admin")),
) -> DemandOut:
    return market_service.create_demand(session, payload, user.username)


@router.patch("/demands/{demand_id}", response_model=DemandOut)
def patch_demand(
    demand_id: str,
    payload: DemandUpdate,
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("admin")),
) -> DemandOut:
    return market_service.update_demand(session, demand_id, payload)


@router.post("/demands/{demand_id}/interest", response_model=InterestOut, status_code=201)
def post_interest(
    demand_id: str,
    payload: InterestCreate,
    session: Session = Depends(get_db),
    user: UserRecord = Depends(require_roles("beekeeper")),
) -> InterestOut:
    if not user.beekeeper_id:
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Beekeeper profile is missing.")
    return market_service.express_interest(session, demand_id, payload, user.beekeeper_id)


@router.get("/prices", response_model=list[SaleOut])
def get_prices(
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("beekeeper", "officer", "admin")),
) -> list[SaleOut]:
    return market_service.list_sales(session)


@router.post("/sales", response_model=SaleOut, status_code=201)
def post_sale(
    payload: SaleCreate,
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("admin")),
) -> SaleOut:
    return market_service.record_sale(session, payload)
