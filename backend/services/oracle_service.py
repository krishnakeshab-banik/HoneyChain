"""Weight oracle: batch declaration vs sensor-corroborated harvest sum."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.models.harvest import HarvestRecord
from backend.models.oracle import OracleEventRecord

# 10% band around the summed sensor-logged harvest weights.
ORACLE_TOLERANCE_PCT = 10.0


@dataclass(frozen=True)
class OracleResult:
    passed: bool
    status: str
    reason: str
    declared_weight_kg: float
    sensor_logged_sum_kg: float
    tolerance_pct: float


def evaluate_weight(
    declared_weight_kg: float,
    harvests: list[HarvestRecord],
) -> OracleResult:
    if not harvests:
        return OracleResult(
            passed=False,
            status="rejected",
            reason="Batch has no linked harvests.",
            declared_weight_kg=declared_weight_kg,
            sensor_logged_sum_kg=0.0,
            tolerance_pct=ORACLE_TOLERANCE_PCT,
        )

    sensor_sum = sum(item.sensor_logged_weight_kg for item in harvests)
    if sensor_sum <= 0:
        return OracleResult(
            passed=False,
            status="rejected",
            reason="Sensor-logged harvest weight sum is zero.",
            declared_weight_kg=declared_weight_kg,
            sensor_logged_sum_kg=sensor_sum,
            tolerance_pct=ORACLE_TOLERANCE_PCT,
        )

    delta_pct = abs(declared_weight_kg - sensor_sum) / sensor_sum * 100.0
    if delta_pct > ORACLE_TOLERANCE_PCT:
        return OracleResult(
            passed=False,
            status="rejected",
            reason=(
                f"Declared weight {declared_weight_kg:.3f} kg differs from "
                f"sensor-logged harvest sum {sensor_sum:.3f} kg "
                f"by {delta_pct:.1f}% (limit {ORACLE_TOLERANCE_PCT:.1f}%)."
            ),
            declared_weight_kg=declared_weight_kg,
            sensor_logged_sum_kg=sensor_sum,
            tolerance_pct=ORACLE_TOLERANCE_PCT,
        )

    return OracleResult(
        passed=True,
        status="passed",
        reason=(
            f"Declared weight {declared_weight_kg:.3f} kg is within "
            f"{ORACLE_TOLERANCE_PCT:.1f}% of sensor-logged sum "
            f"{sensor_sum:.3f} kg (delta {delta_pct:.1f}%)."
        ),
        declared_weight_kg=declared_weight_kg,
        sensor_logged_sum_kg=sensor_sum,
        tolerance_pct=ORACLE_TOLERANCE_PCT,
    )


def log_decision(session: Session, batch_id: str, result: OracleResult) -> OracleEventRecord:
    event = OracleEventRecord(
        batch_id=batch_id,
        decided_at=datetime.now(timezone.utc),
        status=result.status,
        reason=result.reason,
        declared_weight_kg=result.declared_weight_kg,
        sensor_logged_sum_kg=result.sensor_logged_sum_kg,
        tolerance_pct=result.tolerance_pct,
    )
    session.add(event)
    session.flush()
    return event
