"""Reference data that must exist so the original hive list still works."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.assignment import HiveAssignmentRecord
from backend.models.beekeeper import BeekeeperRecord
from backend.models.hive import HiveRecord
from backend.models.market import DemandInterestRecord, DemandRecord, SaleRecord
from backend.models.user import UserRecord
from backend.services.auth_service import hash_password


# DE-001 was previously labelled data_source="real_dataset" and
# source_reference="German Smart Beehive Dataset" but the repo never
# ingested that dataset, so the hive was a dead registered entity.
# Standing rule: no dead UI. There is no dataset file to wire, so DE-001
# is reclassified as simulated and the multi-hive simulator feeds it.
# This changes GET /api/hives for DE-001's provenance fields only.
SEED_HIVES: list[dict[str, str | bool]] = [
    {
        "hive_id": "DE-001",
        "name": "Bremen Demonstration Hive",
        "country": "Germany",
        "region": "Bremen",
        "bee_species": "Apis mellifera",
        "climate_zone": "temperate",
        "data_source": "simulated",
        "source_reference": "HoneyChain Simulator (temperate profile)",
        "active": True,
    },
    {
        "hive_id": "IN-WB-001",
        "name": "West Bengal Demo Hive",
        "country": "India",
        "region": "West Bengal",
        "bee_species": "Apis cerana",
        "climate_zone": "humid_subtropical",
        "data_source": "simulated",
        "source_reference": "HoneyChain Simulator",
        "active": True,
    },
]

SEED_BEEKEEPERS: list[dict[str, str]] = [
    {
        "beekeeper_id": "BK-DE-01",
        "name": "Lena Hoffmann",
        "cluster": "Bremen Cooperative",
        "region": "Bremen",
    },
    {
        "beekeeper_id": "BK-WB-01",
        "name": "Ananya Roy",
        "cluster": "West Bengal Producer Cluster",
        "region": "West Bengal",
    },
]


SEED_ASSIGNMENTS = {
    "IN-WB-001": "BK-WB-01",
    "DE-001": "BK-DE-01",
}

SEED_USERS = [
    {
        "username": "beekeeper",
        "password": "Beekeeper123!",
        "display_name": "Ananya Roy",
        "role": "beekeeper",
        "beekeeper_id": "BK-WB-01",
        "cluster": "West Bengal Producer Cluster",
        "region": "West Bengal",
        "language": "en",
        "email": "ananya@honeychain.demo",
        "phone": "+91-98000-00001",
    },
    {
        "username": "officer",
        "password": "Officer123!",
        "display_name": "Ravi Menon",
        "role": "officer",
        "beekeeper_id": None,
        "cluster": "West Bengal Producer Cluster",
        "region": "West Bengal",
        "language": "en",
        "email": "ravi@honeychain.demo",
        "phone": "+91-98000-00002",
    },
    {
        "username": "lab",
        "password": "Lab123!",
        "display_name": "Dr. Meera Iyer",
        "role": "lab",
        "beekeeper_id": None,
        "cluster": None,
        "region": None,
        "language": "en",
        "email": "meera@honeychain.demo",
        "phone": "+91-98000-00003",
    },
    {
        "username": "admin",
        "password": "Admin123!",
        "display_name": "KVIC Admin",
        "role": "admin",
        "beekeeper_id": None,
        "cluster": None,
        "region": None,
        "language": "en",
        "email": "admin@honeychain.demo",
        "phone": "+91-98000-00004",
    },
]


def seed_reference_data(session: Session) -> None:
    for row in SEED_HIVES:
        existing = session.get(HiveRecord, row["hive_id"])
        if existing is None:
            session.add(HiveRecord(**row))
    for row in SEED_BEEKEEPERS:
        existing = session.get(BeekeeperRecord, row["beekeeper_id"])
        if existing is None:
            session.add(BeekeeperRecord(**row))
    session.flush()
    for hive_id, beekeeper_id in SEED_ASSIGNMENTS.items():
        if session.get(HiveAssignmentRecord, hive_id) is None:
            session.add(HiveAssignmentRecord(hive_id=hive_id, beekeeper_id=beekeeper_id))
    for row in SEED_USERS:
        if session.get(UserRecord, row["username"]) is None:
            session.add(
                UserRecord(
                    username=row["username"],
                    password_hash=hash_password(row["password"]),
                    display_name=row["display_name"],
                    role=row["role"],
                    beekeeper_id=row["beekeeper_id"],
                    cluster=row["cluster"],
                    region=row["region"],
                    language=row["language"],
                    email=row.get("email"),
                    phone=row.get("phone"),
                    active=True,
                )
            )
    _purge_placeholder_market(session)


def _purge_placeholder_market(session: Session) -> None:
    """Remove fictional seed listings that were never tied to a ledgered batch."""

    for sale_id in ("SALE-SEED-01", "SALE-SEED-02"):
        row = session.get(SaleRecord, sale_id)
        if row is not None:
            session.delete(row)
    for demand_id in ("DEM-WB-01", "DEM-MH-01"):
        interests = session.scalars(
            select(DemandInterestRecord).where(DemandInterestRecord.demand_id == demand_id)
        ).all()
        for interest in interests:
            session.delete(interest)
        demand = session.get(DemandRecord, demand_id)
        if demand is not None:
            session.delete(demand)
    leftover = session.scalars(select(SaleRecord).where(SaleRecord.batch_id == "BT-SEED-PLACEHOLDER")).all()
    for row in leftover:
        session.delete(row)


def list_seeded_hive_ids(session: Session) -> list[str]:
    rows = session.scalars(select(HiveRecord.hive_id).order_by(HiveRecord.hive_id)).all()
    return list(rows)
