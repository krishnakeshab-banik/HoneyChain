from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class BatchHarvestRecord(Base):
    __tablename__ = "batch_harvests"

    batch_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("batches.batch_id"),
        primary_key=True,
    )
    harvest_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("harvests.harvest_id"),
        primary_key=True,
    )


class BatchRecord(Base):
    __tablename__ = "batches"

    batch_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    processing_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    declared_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    lab_test_result: Mapped[str] = mapped_column(String(20), nullable=False)
    lab_notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    oracle_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    oracle_reason: Mapped[str] = mapped_column(Text, default="", nullable=False)

    harvests: Mapped[list["HarvestRecord"]] = relationship(
        secondary="batch_harvests",
        back_populates="batches",
    )
    packages: Mapped[list["PackageRecord"]] = relationship(back_populates="batch")
    ledger_blocks: Mapped[list["LedgerBlockRecord"]] = relationship(back_populates="batch")
    oracle_events: Mapped[list["OracleEventRecord"]] = relationship(back_populates="batch")
