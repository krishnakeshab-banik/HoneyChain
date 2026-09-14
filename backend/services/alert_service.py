from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.alert import AlertRecord


def queue_whatsapp_alert(session: Session, hive_id: str, message: str, recipient_role: str) -> dict[str, str]:
    """Store a WhatsApp-shaped alert. No message is sent to a real phone network."""

    record = AlertRecord(
        alert_id=f"AL-{uuid4().hex[:10]}",
        hive_id=hive_id,
        channel="whatsapp",
        message=message,
        created_at=datetime.now(timezone.utc),
        recipient_role=recipient_role,
    )
    session.add(record)
    session.flush()
    return {
        "alert_id": record.alert_id,
        "channel": record.channel,
        "status": "queued_local_only",
        "message": record.message,
    }


def list_alerts(session: Session) -> list[dict[str, str]]:
    rows = session.scalars(select(AlertRecord).order_by(AlertRecord.created_at.desc())).all()
    return [
        {
            "alert_id": row.alert_id,
            "hive_id": row.hive_id,
            "channel": row.channel,
            "message": row.message,
            "created_at": row.created_at.isoformat(),
            "recipient_role": row.recipient_role,
        }
        for row in rows
    ]
