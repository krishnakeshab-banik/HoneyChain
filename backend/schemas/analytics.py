from __future__ import annotations

from pydantic import BaseModel


class MapPin(BaseModel):
    beekeeper_id: str
    name: str
    region: str
    cluster: str
    latitude: float
    longitude: float
    hive_count: int
    sale_kg: float
    sale_value_inr: float


class NamedValue(BaseModel):
    label: str
    value: float


class AdminAnalyticsOut(BaseModel):
    pins: list[MapPin]
    sales_by_region: list[NamedValue]
    volume_by_day: list[NamedValue]
    batch_status: list[NamedValue]
    hive_count: int
    sale_count: int
    sale_kg: float
    sale_value_inr: float
    flagged_scans: int
    report: str


class SellerAnalyticsOut(BaseModel):
    beekeeper_id: str
    name: str
    region: str
    hive_count: int
    harvest_count: int
    harvest_kg: float
    sale_kg: float
    sale_value_inr: float
    open_interests: int
    volume_by_day: list[NamedValue]
    report: str
