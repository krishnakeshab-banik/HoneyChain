from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class SensorReadingRecord(Base):
    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hive_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("hives.hive_id"),
        nullable=False,
        index=True,
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    inside_temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    outside_temperature_c: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)

    hive: Mapped["HiveRecord"] = relationship(back_populates="sensor_readings")
