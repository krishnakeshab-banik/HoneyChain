from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class BeekeeperRecord(Base):
    __tablename__ = "beekeepers"

    beekeeper_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cluster: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)

    harvests: Mapped[list["HarvestRecord"]] = relationship(back_populates="beekeeper")
