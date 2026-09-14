from __future__ import annotations

from pydantic import BaseModel


class PublicStats(BaseModel):
    hives_connected: int
    batches_verified: int
    flagged_attempts: int


class ImpactPoint(BaseModel):
    label: str
    hives_connected: int
    batches_verified: int
    flagged_attempts: int


class PublicImpact(BaseModel):
    points: list[ImpactPoint]
