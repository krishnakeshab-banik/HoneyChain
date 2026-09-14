from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.harvest import HarvestOut


class BatchCreate(BaseModel):
    batch_id: str = Field(..., min_length=3, max_length=50)
    harvest_ids: list[str] = Field(..., min_length=1)
    processing_date: datetime
    declared_weight_kg: float = Field(..., gt=0, le=2000)
    lab_test_result: Literal["pass", "fail", "pending"]
    lab_notes: str = ""


class BatchUpdate(BaseModel):
    declared_weight_kg: float | None = Field(default=None, gt=0, le=2000)
    lab_test_result: Literal["pass", "fail", "pending"] | None = None
    lab_notes: str | None = None
    harvest_ids: list[str] | None = Field(default=None, min_length=1)


class BatchOut(BaseModel):
    batch_id: str
    processing_date: datetime
    declared_weight_kg: float
    lab_test_result: str
    lab_notes: str
    status: str
    oracle_status: str
    oracle_reason: str
    harvests: list[HarvestOut]


class OracleDecisionOut(BaseModel):
    batch_id: str
    status: str
    reason: str
    declared_weight_kg: float
    sensor_logged_sum_kg: float
    tolerance_pct: float
    decided_at: datetime
