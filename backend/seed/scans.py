"""Small consumer-scan history on the seeded package."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.scan import ScanRecord
from backend.seed.ledger import PKG

# Kolkata then Bremen within 90 minutes — CloneWatch should flag distance.
SCANS = [
    {
        "scanned_at": datetime(2026, 9, 13, 18, 0, tzinfo=timezone.utc),
        "latitude": 22.5726,
        "longitude": 88.3639,
        "location_label": "Kolkata",
        "flagged": False,
        "flag_reason": "",
    },
    {
        "scanned_at": datetime(2026, 9, 13, 19, 10, tzinfo=timezone.utc),
        "latitude": 53.0793,
        "longitude": 8.8017,
        "location_label": "Bremen",
        "flagged": True,
        "flag_reason": "Scanned 7400 km from Kolkata within 1.17 hours.",
    },
]


def seed_scans(session: Session) -> None:
    existing = session.scalars(select(ScanRecord).where(ScanRecord.package_id == PKG)).all()
    if existing:
        return
    for row in SCANS:
        session.add(ScanRecord(package_id=PKG, **row))
    session.flush()
