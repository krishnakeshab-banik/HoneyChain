from __future__ import annotations

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base

ROLES = ("beekeeper", "officer", "lab", "admin", "distributor")


class UserRecord(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(80), primary_key=True)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    beekeeper_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cluster: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="en", nullable=False)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
