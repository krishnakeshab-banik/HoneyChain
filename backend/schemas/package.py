from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PackageCreate(BaseModel):
    package_id: str = Field(..., min_length=3, max_length=50)
    batch_id: str = Field(..., min_length=3, max_length=50)
    verify_base_url: str = Field(
        default="http://127.0.0.1:5173/verify",
        description="React UI origin encoded into the QR code.",
    )


class PackageOut(BaseModel):
    package_id: str
    batch_id: str
    qr_reference: str
    qr_image_path: str
    created_at: datetime


class ScanLocationIn(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    location_label: str = Field(..., min_length=2, max_length=120)


class HiveHealthAtHarvest(BaseModel):
    hive_id: str
    inside_temperature_c: float | None
    humidity_pct: float | None
    weight_kg: float | None
    status_label: str


class HarvestPassportRow(BaseModel):
    harvest_id: str
    hive_id: str
    raw_weight_kg: float
    harvested_at: datetime


class VerifyPassport(BaseModel):
    package_id: str
    batch_id: str
    beekeeper_id: str
    beekeeper_name: str
    cluster: str
    harvest_dates: list[datetime]
    harvests: list[HarvestPassportRow] = []
    declared_weight_kg: float = 0
    lab_test_result: str
    hive_health_at_harvest: list[HiveHealthAtHarvest]
    ledger_verified: bool
    ledger_detail: str
    qr_reference: str
    scan_id: int
    scan_flagged: bool
    scan_flag_reason: str
