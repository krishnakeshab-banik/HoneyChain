from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class HarvestRecord(Base):
    __tablename__ = "harvests"

    harvest_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    hive_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("hives.hive_id"),
        nullable=False,
        index=True,
    )
    beekeeper_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("beekeepers.beekeeper_id"),
        nullable=False,
    )
    harvested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    raw_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    moisture_pct: Mapped[float] = mapped_column(Float, nullable=False)
    hive_weight_at_harvest_kg: Mapped[float] = mapped_column(Float, nullable=False)
    sensor_logged_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    inside_temperature_c_at_harvest: Mapped[float] = mapped_column(Float, nullable=False)
    humidity_pct_at_harvest: Mapped[float] = mapped_column(Float, nullable=False)

    hive: Mapped["HiveRecord"] = relationship(back_populates="harvests")
    beekeeper: Mapped["BeekeeperRecord"] = relationship(back_populates="harvests")
    batches: Mapped[list["BatchRecord"]] = relationship(
        secondary="batch_harvests",
        back_populates="harvests",
    )
