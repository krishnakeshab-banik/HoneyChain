"""Compose and reset the one-time demo story. Idempotent."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.batch import BatchHarvestRecord, BatchRecord
from backend.models.harvest import HarvestRecord
from backend.models.ledger import LedgerBlockRecord
from backend.models.oracle import OracleEventRecord
from backend.models.market import DemandInterestRecord, DemandRecord, SaleRecord
from backend.models.package import PackageRecord
from backend.models.scan import ScanRecord
from backend.models.sensor import SensorReadingRecord
from backend.seed.hives import PROFILES, seed_extra_hives, seed_telemetry_history
from backend.seed.ledger import BT_ONE, BT_TWO, HV_DE, HV_WB, PKG, seed_harvests_and_ledger
from backend.seed.market import DEM, INT, SALE, seed_market
from backend.seed.scans import seed_scans

SKIP_ENV = "HONEYCHAIN_SKIP_DEMO_SEED"


def demo_seed_enabled() -> bool:
    return os.environ.get(SKIP_ENV, "").strip() not in {"1", "true", "yes"}


def apply_demo_story(session: Session) -> None:
    seed_extra_hives(session)
    seed_telemetry_history(session)
    seed_harvests_and_ledger(session)
    seed_market(session)
    seed_scans(session)


def seed_demo_story(session: Session) -> None:
    if not demo_seed_enabled():
        return
    apply_demo_story(session)


def reset_demo_story(session: Session) -> None:
    """Remove demo-tagged rows so the story can be seeded again."""

    live_blocks = session.scalars(
        select(LedgerBlockRecord).where(LedgerBlockRecord.batch_id.notin_([BT_ONE, BT_TWO]))
    ).all()
    if live_blocks:
        raise RuntimeError(
            "Live ledger blocks exist after the demo seed. "
            "Resetting would break the hash-chain. Use a fresh honeychain.db."
        )
    for scan in session.scalars(select(ScanRecord).where(ScanRecord.package_id == PKG)).all():
        session.delete(scan)
    package = session.get(PackageRecord, PKG)
    if package is not None:
        session.delete(package)
    sale = session.get(SaleRecord, SALE)
    if sale is not None:
        session.delete(sale)
    interest = session.get(DemandInterestRecord, INT)
    if interest is not None:
        session.delete(interest)
    demand = session.get(DemandRecord, DEM)
    if demand is not None:
        session.delete(demand)
    for batch_id in (BT_TWO, BT_ONE):
        for event in session.scalars(select(OracleEventRecord).where(OracleEventRecord.batch_id == batch_id)).all():
            session.delete(event)
        for block in session.scalars(select(LedgerBlockRecord).where(LedgerBlockRecord.batch_id == batch_id)).all():
            session.delete(block)
        links = session.scalars(select(BatchHarvestRecord).where(BatchHarvestRecord.batch_id == batch_id)).all()
        for link in links:
            session.delete(link)
        batch = session.get(BatchRecord, batch_id)
        if batch is not None:
            session.delete(batch)
    for harvest_id in (HV_WB, HV_DE):
        harvest = session.get(HarvestRecord, harvest_id)
        if harvest is not None:
            session.delete(harvest)
    origin = datetime(2026, 9, 13, tzinfo=timezone.utc)
    end = origin.replace(hour=23, minute=59)
    seeded = session.scalars(
        select(SensorReadingRecord)
        .where(SensorReadingRecord.hive_id.in_(list(PROFILES)))
        .where(SensorReadingRecord.timestamp >= origin)
        .where(SensorReadingRecord.timestamp <= end)
        .where(SensorReadingRecord.source == "simulated")
    ).all()
    for row in seeded:
        session.delete(row)
    session.flush()
