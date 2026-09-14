"""Market listings tied to a real ledgered demo batch — not placeholders."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.models.market import DemandInterestRecord, DemandRecord, SaleRecord
from backend.seed.ledger import BT_ONE

DEM = "DEM-DEMO-WB"
SALE = "SALE-DEMO-01"
INT = "INT-DEMO-01"


def seed_market(session: Session) -> None:
    if session.get(DemandRecord, DEM) is None:
        session.add(
            DemandRecord(
                demand_id=DEM,
                buyer_name="Howrah Cooperative Buyer",
                region="West Bengal",
                quantity_kg=12.0,
                price_min_inr=280.0,
                price_max_inr=340.0,
                notes="One-time demo demand. New interest after this is live.",
                posted_by="officer",
                posted_at=datetime(2026, 9, 13, 16, 0, tzinfo=timezone.utc),
                status="open",
            )
        )
        session.flush()
    if session.get(DemandInterestRecord, INT) is None:
        session.add(
            DemandInterestRecord(
                interest_id=INT,
                demand_id=DEM,
                beekeeper_id="BK-WB-01",
                offered_kg=6.2,
                created_at=datetime(2026, 9, 13, 16, 30, tzinfo=timezone.utc),
            )
        )
        session.flush()
    if session.get(SaleRecord, SALE) is None:
        session.add(
            SaleRecord(
                sale_id=SALE,
                batch_id=BT_ONE,
                demand_id=DEM,
                region="West Bengal",
                season="2026 monsoon",
                price_per_kg_inr=310.0,
                quantity_kg=6.2,
                buyer_name="Howrah Cooperative Buyer",
                recorded_at=datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc),
            )
        )
    session.flush()
