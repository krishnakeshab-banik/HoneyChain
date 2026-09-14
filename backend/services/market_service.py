from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.batch import BatchRecord
from backend.models.market import DemandInterestRecord, DemandRecord, SaleRecord
from backend.schemas.market import DemandCreate, DemandOut, DemandUpdate, InterestCreate, InterestOut, SaleCreate, SaleOut


def _demand_out(session: Session, record: DemandRecord) -> DemandOut:
    count = session.scalar(
        select(func.count()).select_from(DemandInterestRecord).where(
            DemandInterestRecord.demand_id == record.demand_id
        )
    )
    return DemandOut(
        demand_id=record.demand_id,
        buyer_name=record.buyer_name,
        region=record.region,
        quantity_kg=record.quantity_kg,
        price_min_inr=record.price_min_inr,
        price_max_inr=record.price_max_inr,
        notes=record.notes,
        posted_by=record.posted_by,
        posted_at=record.posted_at,
        status=record.status,
        interest_count=int(count or 0),
    )


def create_demand(session: Session, payload: DemandCreate, posted_by: str) -> DemandOut:
    if session.get(DemandRecord, payload.demand_id) is not None:
        raise HTTPException(status_code=409, detail=f"Demand '{payload.demand_id}' already exists.")
    if payload.price_max_inr < payload.price_min_inr:
        raise HTTPException(status_code=422, detail="price_max_inr must be at least price_min_inr.")
    record = DemandRecord(
        demand_id=payload.demand_id,
        buyer_name=payload.buyer_name,
        region=payload.region,
        quantity_kg=payload.quantity_kg,
        price_min_inr=payload.price_min_inr,
        price_max_inr=payload.price_max_inr,
        notes=payload.notes,
        posted_by=posted_by,
        posted_at=datetime.now(timezone.utc),
        status="open",
    )
    session.add(record)
    session.flush()
    return _demand_out(session, record)


def update_demand(session: Session, demand_id: str, payload: DemandUpdate) -> DemandOut:
    record = session.get(DemandRecord, demand_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Demand '{demand_id}' does not exist.")
    data = payload.model_dump(exclude_unset=True)
    if "price_min_inr" in data or "price_max_inr" in data:
        low = data.get("price_min_inr", record.price_min_inr)
        high = data.get("price_max_inr", record.price_max_inr)
        if high < low:
            raise HTTPException(status_code=422, detail="price_max_inr must be at least price_min_inr.")
    for key, value in data.items():
        setattr(record, key, value)
    session.flush()
    return _demand_out(session, record)


def list_demands(session: Session) -> list[DemandOut]:
    rows = session.scalars(select(DemandRecord).order_by(DemandRecord.posted_at.desc())).all()
    return [_demand_out(session, row) for row in rows]


def express_interest(
    session: Session,
    demand_id: str,
    payload: InterestCreate,
    beekeeper_id: str,
) -> InterestOut:
    demand = session.get(DemandRecord, demand_id)
    if demand is None:
        raise HTTPException(status_code=404, detail=f"Demand '{demand_id}' does not exist.")
    if demand.status != "open":
        raise HTTPException(status_code=409, detail="This demand is no longer open.")
    record = DemandInterestRecord(
        interest_id=f"INT-{uuid4().hex[:10]}",
        demand_id=demand_id,
        beekeeper_id=beekeeper_id,
        offered_kg=payload.offered_kg,
        created_at=datetime.now(timezone.utc),
    )
    session.add(record)
    session.flush()
    return InterestOut(
        interest_id=record.interest_id,
        demand_id=record.demand_id,
        beekeeper_id=record.beekeeper_id,
        offered_kg=record.offered_kg,
        created_at=record.created_at,
    )


def list_sales(session: Session) -> list[SaleOut]:
    rows = session.scalars(select(SaleRecord).order_by(SaleRecord.recorded_at.desc())).all()
    rows = [row for row in rows if row.batch_id != "BT-SEED-PLACEHOLDER" and not str(row.sale_id).startswith("SALE-SEED")]
    return [
        SaleOut(
            sale_id=row.sale_id,
            batch_id=row.batch_id,
            demand_id=row.demand_id,
            region=row.region,
            season=row.season,
            price_per_kg_inr=row.price_per_kg_inr,
            quantity_kg=row.quantity_kg,
            buyer_name=row.buyer_name,
            recorded_at=row.recorded_at,
        )
        for row in rows
    ]


def record_sale(session: Session, payload: SaleCreate) -> SaleOut:
    if session.get(SaleRecord, payload.sale_id) is not None:
        raise HTTPException(status_code=409, detail=f"Sale '{payload.sale_id}' already exists.")
    batch = session.get(BatchRecord, payload.batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail=f"Batch '{payload.batch_id}' does not exist.")
    if batch.status != "committed":
        raise HTTPException(status_code=409, detail="Only ledgered batches can be linked to a sale.")
    record = SaleRecord(
        sale_id=payload.sale_id,
        batch_id=payload.batch_id,
        demand_id=payload.demand_id,
        region=payload.region,
        season=payload.season,
        price_per_kg_inr=payload.price_per_kg_inr,
        quantity_kg=payload.quantity_kg,
        buyer_name=payload.buyer_name,
        recorded_at=datetime.now(timezone.utc),
    )
    session.add(record)
    session.flush()
    return SaleOut(
        sale_id=record.sale_id,
        batch_id=record.batch_id,
        demand_id=record.demand_id,
        region=record.region,
        season=record.season,
        price_per_kg_inr=record.price_per_kg_inr,
        quantity_kg=record.quantity_kg,
        buyer_name=record.buyer_name,
        recorded_at=record.recorded_at,
    )
