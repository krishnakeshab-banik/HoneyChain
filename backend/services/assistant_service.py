"""Role-scoped context for the voice/text assistant."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models.user import UserRecord
from backend.services import me_service
from backend.services.ml_service import ml_service
from backend.services.sensor_service import latest_reading


PRODUCT_KNOWLEDGE = """
HoneyChain product (facts, not this user's private numbers):
- Smart-hive telemetry plus harvest-to-jar traceability. Ledger is a local SHA-256 hash-chain, not a public blockchain.
- Demo roles: beekeeper, cluster/KVIC officer, lab inspector, admin. Consumers verify honey with no login.
- Beekeeper flow: watch hive → log harvest → officer drafts a batch (pending lab) → lab records pass/fail → officer oracle-commits → package + QR → consumer verify.
- Oracle: declared batch weight must stay within 10% of sensor-logged harvest kilograms.
- Lab desk queue is draft batches with lab_test_result pending. Commit is blocked until a recorded pass.
- Consumer Verify recomputes the ledger live and logs a scan. CloneWatch flags too-many scans, implausible travel, or oracle-failed batches.
- Market Linkage shows live demand separately from one-time example/seed listings.
- Insights: colony health RandomForest and yield models trained on MSPB D1/D2. Public model card shows honest held-out health accuracy 40%.
- UI languages: English, Hindi, Bengali, Tamil, Kannada, Telugu, Marathi. IDs and hashes stay untranslated.
- Guided tour reads each step aloud in the selected language. Ask HoneyChain answers in the language of the question.
""".strip()


def user_context(session: Session, user: UserRecord) -> str:
    hives = me_service.hives_for_user(session, user)
    harvests = me_service.harvests_for_user(session, user)
    lines = [
        f"Signed-in user: {user.display_name} ({user.username})",
        f"Role: {user.role}",
        f"Region: {user.region or 'not set'}",
        f"Cluster: {user.cluster or 'not set'}",
        f"Hives visible to this user ({len(hives)}):",
    ]
    if not hives:
        lines.append("- none assigned yet")
    for hive in hives:
        reading = latest_reading(session, hive.hive_id)
        if reading is None:
            lines.append(f"- {hive.hive_id} ({hive.name}): awaiting sensor data")
            continue
        try:
            insights = ml_service.insights_for_hive(session, hive.hive_id, attach_ai=False)
            status = insights.health.status
            forecast = insights.forecast.predicted_weight_kg
        except Exception:
            status = "not yet available"
            forecast = None
        extra = f", forecast {forecast:.2f} kg" if forecast is not None else ""
        lines.append(
            f"- {hive.hive_id} ({hive.name}): live {reading.weight_kg:.2f} kg, "
            f"{reading.inside_temperature_c:.1f} °C, {reading.humidity_pct:.1f}% humidity, "
            f"colony status {status}{extra}"
        )
    pending = [row for row in harvests if row.get("status") == "pending"]
    lines.append(f"Harvests visible: {len(harvests)} total, {len(pending)} still pending (not on the ledger).")
    for row in harvests[:8]:
        lines.append(
            f"- {row['harvest_id']} hive {row['hive_id']} {row['raw_weight_kg']} kg status {row['status']}"
        )
    lines.append("Do not mention any hive, harvest, or person that is not listed above.")
    lines.append(PRODUCT_KNOWLEDGE)
    return "\n".join(lines)
