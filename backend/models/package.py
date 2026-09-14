from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class PackageRecord(Base):
    __tablename__ = "packages"

    package_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    batch_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("batches.batch_id"),
        nullable=False,
        index=True,
    )
    qr_reference: Mapped[str] = mapped_column(String(300), nullable=False)
    qr_image_path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    batch: Mapped["BatchRecord"] = relationship(back_populates="packages")
    scans: Mapped[list["ScanRecord"]] = relationship(
        back_populates="package",
        cascade="all, delete-orphan",
    )
