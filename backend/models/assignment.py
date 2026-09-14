from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class HiveAssignmentRecord(Base):
    """Maps a hive to a beekeeper without changing the public Hive JSON contract."""

    __tablename__ = "hive_assignments"

    hive_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("hives.hive_id"),
        primary_key=True,
    )
    beekeeper_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("beekeepers.beekeeper_id"),
        nullable=False,
    )
