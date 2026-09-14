from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class AlertRecord(Base):
    __tablename__ = "alerts"

    alert_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    hive_id: Mapped[str] = mapped_column(String(50), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recipient_role: Mapped[str] = mapped_column(String(32), nullable=False)
