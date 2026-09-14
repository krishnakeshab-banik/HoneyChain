from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class DemandRecord(Base):
    __tablename__ = "market_demands"

    demand_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    buyer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    price_min_inr: Mapped[float] = mapped_column(Float, nullable=False)
    price_max_inr: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    posted_by: Mapped[str] = mapped_column(String(80), nullable=False)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="open", nullable=False)


class DemandInterestRecord(Base):
    __tablename__ = "market_interests"

    interest_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    demand_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("market_demands.demand_id"),
        nullable=False,
    )
    beekeeper_id: Mapped[str] = mapped_column(String(50), nullable=False)
    offered_kg: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SaleRecord(Base):
    __tablename__ = "market_sales"

    sale_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(50), nullable=False)
    demand_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    season: Mapped[str] = mapped_column(String(40), nullable=False)
    price_per_kg_inr: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_kg: Mapped[float] = mapped_column(Float, nullable=False)
    buyer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
