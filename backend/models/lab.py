from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class LabResultRecord(Base):
    __tablename__ = "lab_results"

    result_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    batch_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("batches.batch_id"),
        nullable=False,
        index=True,
    )
    moisture_pct: Mapped[float] = mapped_column(Float, nullable=False)
    purity_pct: Mapped[float] = mapped_column(Float, nullable=False)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    inspector: Mapped[str] = mapped_column(String(80), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
