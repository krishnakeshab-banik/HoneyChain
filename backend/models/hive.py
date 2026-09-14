from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class HiveRecord(Base):
    __tablename__ = "hives"

    hive_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    bee_species: Mapped[str] = mapped_column(String(100), nullable=False)
    climate_zone: Mapped[str] = mapped_column(String(100), nullable=False)
    data_source: Mapped[str] = mapped_column(String(32), nullable=False)
    source_reference: Mapped[str] = mapped_column(String(200), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sensor_readings: Mapped[list["SensorReadingRecord"]] = relationship(
        back_populates="hive",
        cascade="all, delete-orphan",
    )
    harvests: Mapped[list["HarvestRecord"]] = relationship(
        back_populates="hive",
    )
