"""Live admin/seller analytics from SQLite — no invented market figures."""

from __future__ import annotations

from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.models.assignment import HiveAssignmentRecord
from backend.models.batch import BatchHarvestRecord, BatchRecord
from backend.models.beekeeper import BeekeeperRecord
from backend.models.harvest import HarvestRecord
from backend.models.hive import HiveRecord
from backend.models.market import DemandInterestRecord, SaleRecord
from backend.models.scan import ScanRecord
from backend.schemas.analytics import (
    AdminAnalyticsOut,
    MapPin,
    NamedValue,
    SellerAnalyticsOut,
)

REGION_COORDS: dict[str, tuple[float, float]] = {
    "West Bengal": (22.9868, 87.8550),
    "Karnataka": (15.3173, 75.7139),
    "Bremen": (53.0793, 8.8017),
    "Kerala": (10.8505, 76.2711),
    "Maharashtra": (19.7515, 75.7139),
    "Germany": (51.1657, 10.4515),
}


def _coords(region: str) -> tuple[float, float]:
    if region in REGION_COORDS:
        return REGION_COORDS[region]
    return (21.0, 78.0)


def admin_analytics(session: Session) -> AdminAnalyticsOut:
    keepers = session.scalars(select(BeekeeperRecord)).all()
    assignments = session.scalars(select(HiveAssignmentRecord)).all()
    hives_by_keeper: dict[str, int] = defaultdict(int)
    for row in assignments:
        hives_by_keeper[row.beekeeper_id] += 1
    sales = session.scalars(select(SaleRecord)).all()
    harvests = session.scalars(select(HarvestRecord)).all()
    harvest_keeper = {row.harvest_id: row.beekeeper_id for row in harvests}
    links = session.scalars(select(BatchHarvestRecord)).all()
    batch_keepers: dict[str, set[str]] = defaultdict(set)
    for link in links:
        keeper = harvest_keeper.get(link.harvest_id)
        if keeper:
            batch_keepers[link.batch_id].add(keeper)

    kg_by_keeper: dict[str, float] = defaultdict(float)
    value_by_keeper: dict[str, float] = defaultdict(float)
    kg_by_region: dict[str, float] = defaultdict(float)
    by_day: dict[str, float] = defaultdict(float)
    for sale in sales:
        owners = batch_keepers.get(sale.batch_id) or set()
        share = sale.quantity_kg / max(len(owners), 1)
        money = sale.price_per_kg_inr * sale.quantity_kg
        money_share = money / max(len(owners), 1)
        for owner in owners or [None]:
            if owner:
                kg_by_keeper[owner] += share
                value_by_keeper[owner] += money_share
        kg_by_region[sale.region] += sale.quantity_kg
        day = sale.recorded_at.date().isoformat() if sale.recorded_at else "unknown"
        by_day[day] += sale.quantity_kg

    pins = [
        MapPin(
            beekeeper_id=row.beekeeper_id,
            name=row.name,
            region=row.region,
            cluster=row.cluster,
            latitude=_coords(row.region)[0],
            longitude=_coords(row.region)[1],
            hive_count=hives_by_keeper.get(row.beekeeper_id, 0),
            sale_kg=round(kg_by_keeper.get(row.beekeeper_id, 0.0), 2),
            sale_value_inr=round(value_by_keeper.get(row.beekeeper_id, 0.0), 2),
        )
        for row in keepers
    ]
    batches = session.scalars(select(BatchRecord)).all()
    status_counts: dict[str, int] = defaultdict(int)
    for batch in batches:
        status_counts[batch.status] += 1
    flagged = session.scalar(select(func.count()).select_from(ScanRecord).where(ScanRecord.flagged.is_(True))) or 0
    hive_count = session.scalar(select(func.count()).select_from(HiveRecord)) or 0
    sale_kg = sum(row.quantity_kg for row in sales)
    sale_value = sum(row.price_per_kg_inr * row.quantity_kg for row in sales)
    report = (
        f"Live cluster report: {int(hive_count)} hives, {len(sales)} ledger-linked sales "
        f"totalling {sale_kg:.1f} kg (₹{sale_value:.0f}). "
        f"{int(flagged)} consumer scans are flagged. "
        "Map pins use regional centroids, not live GPS. "
        "Sale kilograms are attributed to the beekeeper(s) on each batch's harvests."
    )
    return AdminAnalyticsOut(
        pins=pins,
        sales_by_region=[NamedValue(label=key, value=round(val, 2)) for key, val in sorted(kg_by_region.items())],
        volume_by_day=[NamedValue(label=key, value=round(val, 2)) for key, val in sorted(by_day.items())],
        batch_status=[NamedValue(label=key, value=float(val)) for key, val in sorted(status_counts.items())],
        hive_count=int(hive_count),
        sale_count=len(sales),
        sale_kg=round(sale_kg, 2),
        sale_value_inr=round(sale_value, 2),
        flagged_scans=int(flagged),
        report=report,
    )


def seller_analytics(session: Session, beekeeper_id: str) -> SellerAnalyticsOut:
    keeper = session.get(BeekeeperRecord, beekeeper_id)
    if keeper is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Beekeeper profile is missing.")
    hive_count = session.scalar(
        select(func.count()).select_from(HiveAssignmentRecord).where(HiveAssignmentRecord.beekeeper_id == beekeeper_id)
    ) or 0
    harvests = session.scalars(select(HarvestRecord).where(HarvestRecord.beekeeper_id == beekeeper_id)).all()
    harvest_ids = {row.harvest_id for row in harvests}
    harvest_kg = sum(row.raw_weight_kg for row in harvests)
    links = (
        session.scalars(select(BatchHarvestRecord).where(BatchHarvestRecord.harvest_id.in_(harvest_ids))).all()
        if harvest_ids
        else []
    )
    batch_ids = {row.batch_id for row in links}
    sales = (
        session.scalars(select(SaleRecord).where(SaleRecord.batch_id.in_(batch_ids))).all()
        if batch_ids
        else []
    )
    sale_kg = sum(row.quantity_kg for row in sales)
    sale_value = sum(row.price_per_kg_inr * row.quantity_kg for row in sales)
    interests = session.scalar(
        select(func.count()).select_from(DemandInterestRecord).where(DemandInterestRecord.beekeeper_id == beekeeper_id)
    ) or 0
    by_day: dict[str, float] = defaultdict(float)
    for row in harvests:
        day = row.harvested_at.date().isoformat() if row.harvested_at else "unknown"
        by_day[day] += row.raw_weight_kg
    report = (
        f"{keeper.name} ({keeper.region}): {int(hive_count)} hive(s), {len(harvests)} harvest(s) "
        f"totalling {harvest_kg:.1f} kg extracted. "
        f"Ledger-linked sales on your batches: {sale_kg:.1f} kg (₹{sale_value:.0f}). "
        f"{int(interests)} demand interest(s) recorded. "
        "This is computed from your HoneyChain records only — not a market forecast."
    )
    return SellerAnalyticsOut(
        beekeeper_id=keeper.beekeeper_id,
        name=keeper.name,
        region=keeper.region,
        hive_count=int(hive_count),
        harvest_count=len(harvests),
        harvest_kg=round(harvest_kg, 2),
        sale_kg=round(sale_kg, 2),
        sale_value_inr=round(sale_value, 2),
        open_interests=int(interests),
        volume_by_day=[NamedValue(label=key, value=round(val, 2)) for key, val in sorted(by_day.items())],
        report=report,
    )
