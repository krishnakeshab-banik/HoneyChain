from __future__ import annotations

import math
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.oracle import OracleEventRecord
from backend.models.package import PackageRecord
from backend.models.scan import ScanRecord
from backend.schemas.clonewatch import CloneWatchReport, FlaggedItem
from backend.schemas.package import HiveHealthAtHarvest, ScanLocationIn, VerifyPassport
from backend.services.harvest_service import require_beekeeper
from backend.services.ledger_service import ledger_service
from backend.services.package_service import load_package_with_batch

MAX_SCANS_BEFORE_FLAG = 6
IMPLAUSIBLE_KM = 250.0
IMPLAUSIBLE_HOURS = 2.0


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.asin(min(1.0, math.sqrt(a)))


def _health_label(temp_c: float | None, humidity: float | None) -> str:
    if temp_c is None:
        return "unknown"
    if 33.0 <= temp_c <= 36.0 and humidity is not None and 50.0 <= humidity <= 75.0:
        return "healthy"
    if temp_c < 31.0 or temp_c > 37.5:
        return "needs-inspection"
    return "stressed"


def _evaluate_scan_flags(
    session: Session,
    package: PackageRecord,
    new_scan: ScanRecord,
) -> tuple[bool, str]:
    reasons: list[str] = []

    if package.batch.oracle_status == "rejected":
        reasons.append("Package is linked to a batch that failed oracle validation.")

    prior = session.scalars(
        select(ScanRecord)
        .where(ScanRecord.package_id == package.package_id)
        .where(ScanRecord.id != new_scan.id)
        .order_by(ScanRecord.scanned_at.asc())
    ).all()
    total = len(prior) + 1
    if total > MAX_SCANS_BEFORE_FLAG:
        reasons.append(
            f"Scanned {total} times (limit {MAX_SCANS_BEFORE_FLAG} before flagging)."
        )

    for previous in prior:
        hours = abs(
            (_as_utc(new_scan.scanned_at) - _as_utc(previous.scanned_at)).total_seconds()
        ) / 3600.0
        distance = haversine_km(
            previous.latitude,
            previous.longitude,
            new_scan.latitude,
            new_scan.longitude,
        )
        if distance >= IMPLAUSIBLE_KM and hours <= IMPLAUSIBLE_HOURS:
            reasons.append(
                f"Scanned {distance:.0f} km from {previous.location_label} "
                f"within {hours:.2f} hours."
            )
            break

    return (len(reasons) > 0, " ".join(reasons))


def record_verification(
    session: Session,
    package_id: str,
    location: ScanLocationIn,
) -> VerifyPassport:
    package = load_package_with_batch(session, package_id)
    scan = ScanRecord(
        package_id=package.package_id,
        scanned_at=datetime.now(timezone.utc),
        latitude=location.latitude,
        longitude=location.longitude,
        location_label=location.location_label,
        flagged=False,
        flag_reason="",
    )
    session.add(scan)
    session.flush()

    flagged, reason = _evaluate_scan_flags(session, package, scan)
    scan.flagged = flagged
    scan.flag_reason = reason
    session.flush()

    harvests = list(package.batch.harvests)
    if not harvests:
        raise RuntimeError(f"Committed package {package_id} has no harvests.")

    first_keeper = require_beekeeper(session, harvests[0].beekeeper_id)
    health_rows = [
        HiveHealthAtHarvest(
            hive_id=item.hive_id,
            inside_temperature_c=item.inside_temperature_c_at_harvest,
            humidity_pct=item.humidity_pct_at_harvest,
            weight_kg=item.hive_weight_at_harvest_kg,
            status_label=_health_label(
                item.inside_temperature_c_at_harvest,
                item.humidity_pct_at_harvest,
            ),
        )
        for item in harvests
    ]

    verified, detail = ledger_service.live_batch_verified(session, package.batch_id)
    return VerifyPassport(
        package_id=package.package_id,
        batch_id=package.batch_id,
        beekeeper_id=first_keeper.beekeeper_id,
        beekeeper_name=first_keeper.name,
        cluster=first_keeper.cluster,
        harvest_dates=[item.harvested_at for item in harvests],
        lab_test_result=package.batch.lab_test_result,
        hive_health_at_harvest=health_rows,
        ledger_verified=verified,
        ledger_detail=detail,
        qr_reference=package.qr_reference,
        scan_id=scan.id,
        scan_flagged=scan.flagged,
        scan_flag_reason=scan.flag_reason,
    )


def build_report(session: Session) -> CloneWatchReport:
    items: list[FlaggedItem] = []

    oracle_rows = session.scalars(
        select(OracleEventRecord)
        .where(OracleEventRecord.status == "rejected")
        .order_by(OracleEventRecord.decided_at.desc())
    ).all()
    for row in oracle_rows:
        items.append(
            FlaggedItem(
                kind="oracle_rejection",
                reference_id=row.batch_id,
                reason=row.reason,
                recorded_at=row.decided_at,
                extra={
                    "declared_weight_kg": row.declared_weight_kg,
                    "sensor_logged_sum_kg": row.sensor_logged_sum_kg,
                    "tolerance_pct": row.tolerance_pct,
                },
            )
        )

    scan_rows = session.scalars(
        select(ScanRecord)
        .where(ScanRecord.flagged.is_(True))
        .order_by(ScanRecord.scanned_at.desc())
    ).all()
    for row in scan_rows:
        items.append(
            FlaggedItem(
                kind="anomalous_scan",
                reference_id=row.package_id,
                reason=row.flag_reason,
                recorded_at=row.scanned_at,
                extra={
                    "scan_id": row.id,
                    "location_label": row.location_label,
                    "latitude": row.latitude,
                    "longitude": row.longitude,
                },
            )
        )

    items.sort(key=lambda item: item.recorded_at, reverse=True)
    return CloneWatchReport(
        flagged_items=items,
        oracle_failures=len(oracle_rows),
        flagged_scans=len(scan_rows),
    )
