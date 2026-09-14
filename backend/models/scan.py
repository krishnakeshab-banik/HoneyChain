from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class ScanRecord(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    package_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("packages.package_id"),
        nullable=False,
        index=True,
    )
    scanned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location_label: Mapped[str] = mapped_column(String(120), nullable=False)
    flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    flag_reason: Mapped[str] = mapped_column(Text, default="", nullable=False)

    package: Mapped["PackageRecord"] = relationship(back_populates="scans")
