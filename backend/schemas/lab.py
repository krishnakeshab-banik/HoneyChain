from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class LabResultCreate(BaseModel):
    batch_id: str = Field(..., min_length=3, max_length=50)
    moisture_pct: float = Field(..., ge=0, le=30)
    purity_pct: float = Field(..., ge=0, le=100)
    result: str = Field(..., pattern="^(pass|fail)$")
    notes: str = ""


class LabResultOut(BaseModel):
    result_id: str
    batch_id: str
    moisture_pct: float
    purity_pct: float
    result: str
    notes: str
    inspector: str
    recorded_at: datetime
