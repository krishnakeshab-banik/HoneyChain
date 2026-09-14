from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class FlaggedItem(BaseModel):
    kind: str
    reference_id: str
    reason: str
    recorded_at: datetime
    extra: dict[str, str | int | float | bool]


class CloneWatchReport(BaseModel):
    flagged_items: list[FlaggedItem]
    oracle_failures: int
    flagged_scans: int
