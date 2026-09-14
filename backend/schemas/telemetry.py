"""Pydantic schemas for hive metadata and sensor readings.

Field names and validation bounds match the original backend/models.py
contracts so GET /api/hives, POST /api/sensor-readings, history, and
summary keep the same JSON shape.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Hive(BaseModel):
    hive_id: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    country: str = Field(..., min_length=2, max_length=100)
    region: str = Field(..., min_length=2, max_length=100)
    bee_species: str = Field(..., min_length=3, max_length=100)
    climate_zone: str = Field(..., min_length=3, max_length=100)
    data_source: Literal["real_dataset", "simulated", "manual"]
    source_reference: str = Field(..., min_length=2, max_length=200)
    active: bool = True


class SensorReading(BaseModel):
    hive_id: str = Field(..., min_length=3, max_length=50)
    timestamp: datetime
    inside_temperature_c: float = Field(..., ge=-40, le=85)
    outside_temperature_c: float = Field(..., ge=-50, le=60)
    humidity_pct: float = Field(..., ge=0, le=100)
    weight_kg: float = Field(..., gt=0, le=500)
    source: Literal["real_dataset", "simulated", "manual"]


class SensorReadingStored(BaseModel):
    message: str
    reading: SensorReading


class HiveSummaryLatest(BaseModel):
    timestamp: datetime
    inside_temperature_c: float
    outside_temperature_c: float
    humidity_pct: float
    weight_kg: float
    source: str


class HiveSummary(BaseModel):
    hive_id: str
    reading_count: int
    latest: HiveSummaryLatest | None
    message: str | None = None
