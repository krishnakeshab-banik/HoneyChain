from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class LedgerBlockRecord(Base):
    __tablename__ = "ledger_blocks"

    index: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("batches.batch_id"),
        nullable=False,
        unique=True,
    )
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    block_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    batch: Mapped["BatchRecord"] = relationship(back_populates="ledger_blocks")
