from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class HarvestCreate(BaseModel):
    harvest_id: str = Field(..., min_length=3, max_length=50)
    hive_id: str = Field(..., min_length=3, max_length=50)
    beekeeper_id: str = Field(..., min_length=3, max_length=50)
    harvested_at: datetime
    raw_weight_kg: float = Field(..., gt=0, le=200)
    moisture_pct: float = Field(..., ge=0, le=30)


class HarvestUpdate(BaseModel):
    raw_weight_kg: float | None = Field(default=None, gt=0, le=200)
    moisture_pct: float | None = Field(default=None, ge=0, le=30)
    harvested_at: datetime | None = None


class HarvestOut(BaseModel):
    harvest_id: str
    hive_id: str
    beekeeper_id: str
    harvested_at: datetime
    raw_weight_kg: float
    moisture_pct: float
    hive_weight_at_harvest_kg: float
    sensor_logged_weight_kg: float
    inside_temperature_c_at_harvest: float
    humidity_pct_at_harvest: float


class BeekeeperOut(BaseModel):
    beekeeper_id: str
    name: str
    cluster: str
    region: str
