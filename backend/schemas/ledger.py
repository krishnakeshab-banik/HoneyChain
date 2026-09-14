from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LedgerBlockOut(BaseModel):
    index: int
    batch_id: str
    previous_hash: str
    block_hash: str
    payload_json: str
    created_at: datetime


class ChainIntegrityOut(BaseModel):
    valid: bool
    checked_blocks: int
    failed_index: int | None
    detail: str
    broken_indexes: list[int] = []


class TamperTestOut(BaseModel):
    action: str
    batch_id: str
    stored_weight_kg: float
    committed_weight_kg: float
    integrity: ChainIntegrityOut
    note: str
