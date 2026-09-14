"""Seed two oracle-passed batches onto the real hash-chain."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.models.batch import BatchRecord
from backend.models.harvest import HarvestRecord
from backend.models.package import PackageRecord
from backend.schemas.batch import BatchCreate
from backend.schemas.harvest import HarvestCreate
from backend.schemas.package import PackageCreate
from backend.services import batch_service, harvest_service, package_service

HV_WB = "HV-DEMO-WB"
HV_DE = "HV-DEMO-DE"
BT_ONE = "BT-DEMO-01"
BT_TWO = "BT-DEMO-02"
PKG = "PKG-DEMO-01"


def seed_harvests_and_ledger(session: Session) -> None:
    if session.get(HarvestRecord, HV_WB) is None:
        harvest_service.create_harvest(
            session,
            HarvestCreate(
                harvest_id=HV_WB,
                hive_id="IN-WB-001",
                beekeeper_id="BK-WB-01",
                harvested_at=datetime(2026, 9, 13, 10, 30, tzinfo=timezone.utc),
                raw_weight_kg=6.2,
                moisture_pct=17.4,
            ),
        )
    if session.get(HarvestRecord, HV_DE) is None:
        harvest_service.create_harvest(
            session,
            HarvestCreate(
                harvest_id=HV_DE,
                hive_id="DE-001",
                beekeeper_id="BK-DE-01",
                harvested_at=datetime(2026, 9, 13, 11, 0, tzinfo=timezone.utc),
                raw_weight_kg=5.8,
                moisture_pct=16.8,
            ),
        )
    if session.get(BatchRecord, BT_ONE) is None:
        batch_service.create_batch(
            session,
            BatchCreate(
                batch_id=BT_ONE,
                harvest_ids=[HV_WB],
                processing_date=datetime(2026, 9, 13, 14, 0, tzinfo=timezone.utc),
                declared_weight_kg=6.2,
                lab_test_result="pass",
                lab_notes="Seed lab pass — moisture in range.",
            ),
        )
    one = session.get(BatchRecord, BT_ONE)
    if one is not None and one.status != "committed":
        batch_service.commit_batch(session, BT_ONE)
    if session.get(BatchRecord, BT_TWO) is None:
        batch_service.create_batch(
            session,
            BatchCreate(
                batch_id=BT_TWO,
                harvest_ids=[HV_DE],
                processing_date=datetime(2026, 9, 13, 15, 0, tzinfo=timezone.utc),
                declared_weight_kg=5.8,
                lab_test_result="pass",
                lab_notes="Seed lab pass — temperate hive.",
            ),
        )
    two = session.get(BatchRecord, BT_TWO)
    if two is not None and two.status != "committed":
        batch_service.commit_batch(session, BT_TWO)
    if session.get(PackageRecord, PKG) is None:
        package_service.create_package(
            session,
            PackageCreate(
                package_id=PKG,
                batch_id=BT_ONE,
                verify_base_url="http://127.0.0.1:5173/verify",
            ),
        )
