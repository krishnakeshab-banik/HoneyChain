from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DemandCreate(BaseModel):
    demand_id: str = Field(..., min_length=3, max_length=50)
    buyer_name: str = Field(..., min_length=2, max_length=120)
    region: str = Field(..., min_length=2, max_length=100)
    quantity_kg: float = Field(..., gt=0, le=100000)
    price_min_inr: float = Field(..., ge=0)
    price_max_inr: float = Field(..., ge=0)
    notes: str = ""


class DemandUpdate(BaseModel):
    buyer_name: str | None = None
    region: str | None = None
    quantity_kg: float | None = Field(default=None, gt=0, le=100000)
    price_min_inr: float | None = Field(default=None, ge=0)
    price_max_inr: float | None = Field(default=None, ge=0)
    notes: str | None = None
    status: str | None = Field(default=None, pattern="^(open|closed|approved)$")


class DemandOut(BaseModel):
    demand_id: str
    buyer_name: str
    region: str
    quantity_kg: float
    price_min_inr: float
    price_max_inr: float
    notes: str
    posted_by: str
    posted_at: datetime
    status: str
    interest_count: int


class InterestCreate(BaseModel):
    offered_kg: float = Field(..., gt=0, le=100000)


class InterestOut(BaseModel):
    interest_id: str
    demand_id: str
    beekeeper_id: str
    offered_kg: float
    created_at: datetime


class SaleCreate(BaseModel):
    sale_id: str = Field(..., min_length=3, max_length=50)
    batch_id: str = Field(..., min_length=3, max_length=50)
    demand_id: str | None = None
    region: str
    season: str
    price_per_kg_inr: float = Field(..., ge=0)
    quantity_kg: float = Field(..., gt=0)
    buyer_name: str


class SaleOut(BaseModel):
    sale_id: str
    batch_id: str
    demand_id: str | None
    region: str
    season: str
    price_per_kg_inr: float
    quantity_kg: float
    buyer_name: str
    recorded_at: datetime
