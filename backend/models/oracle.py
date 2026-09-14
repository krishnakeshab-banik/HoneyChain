from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class OracleEventRecord(Base):
    """Every oracle decision is stored, including failures shown in CloneWatch."""

    __tablename__ = "oracle_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("batches.batch_id"),
        nullable=False,
        index=True,
    )
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    declared_weight_kg: Mapped[float] = mapped_column(nullable=False)
    sensor_logged_sum_kg: Mapped[float] = mapped_column(nullable=False)
    tolerance_pct: Mapped[float] = mapped_column(nullable=False)

    batch: Mapped["BatchRecord"] = relationship(back_populates="oracle_events")
