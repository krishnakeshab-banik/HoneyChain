"""SHA-256 hash-chain ledger.

Calling code depends only on this class. A later Hyperledger Fabric or
Polygon adapter can implement the same public methods without changing
routers or other services.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Protocol

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.batch import BatchRecord
from backend.models.ledger import LedgerBlockRecord
from backend.schemas.ledger import ChainIntegrityOut, LedgerBlockOut, TamperTestOut

GENESIS_PREVIOUS_HASH = "0" * 64


class LedgerPort(Protocol):
    """Swap point for a future on-chain implementation."""

    def commit_batch(self, session: Session, batch: BatchRecord) -> LedgerBlockOut: ...

    def get_chain(self, session: Session) -> list[LedgerBlockOut]: ...

    def get_custody(self, session: Session, batch_id: str) -> list[LedgerBlockOut]: ...

    def verify_integrity(self, session: Session) -> ChainIntegrityOut: ...


def _canonical_payload(batch: BatchRecord, previous_hash: str) -> str:
    harvest_ids = sorted(item.harvest_id for item in batch.harvests)
    body = {
        "batch_id": batch.batch_id,
        "declared_weight_kg": batch.declared_weight_kg,
        "harvest_ids": harvest_ids,
        "lab_test_result": batch.lab_test_result,
        "processing_date": batch.processing_date.isoformat(),
        "previous_hash": previous_hash,
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":"))


def compute_block_hash(payload_json: str) -> str:
    return hashlib.sha256(payload_json.encode("utf-8")).hexdigest()


def _to_out(record: LedgerBlockRecord) -> LedgerBlockOut:
    return LedgerBlockOut(
        index=record.index,
        batch_id=record.batch_id,
        previous_hash=record.previous_hash,
        block_hash=record.block_hash,
        payload_json=record.payload_json,
        created_at=record.created_at,
    )


class LedgerService:
    """Local hash-chain stored in SQLite. Not a public blockchain."""

    def commit_batch(self, session: Session, batch: BatchRecord) -> LedgerBlockOut:
        existing = session.scalars(
            select(LedgerBlockRecord).where(LedgerBlockRecord.batch_id == batch.batch_id)
        ).first()
        if existing is not None:
            raise HTTPException(
                status_code=409,
                detail=f"Batch '{batch.batch_id}' is already on the ledger.",
            )

        last = session.scalars(
            select(LedgerBlockRecord).order_by(LedgerBlockRecord.index.desc()).limit(1)
        ).first()
        previous_hash = last.block_hash if last is not None else GENESIS_PREVIOUS_HASH
        payload_json = _canonical_payload(batch, previous_hash)
        block_hash = compute_block_hash(payload_json)
        record = LedgerBlockRecord(
            batch_id=batch.batch_id,
            previous_hash=previous_hash,
            block_hash=block_hash,
            payload_json=payload_json,
            created_at=datetime.now(timezone.utc),
        )
        session.add(record)
        session.flush()
        return _to_out(record)

    def get_chain(self, session: Session) -> list[LedgerBlockOut]:
        rows = session.scalars(
            select(LedgerBlockRecord).order_by(LedgerBlockRecord.index.asc())
        ).all()
        return [_to_out(row) for row in rows]

    def get_custody(self, session: Session, batch_id: str) -> list[LedgerBlockOut]:
        rows = session.scalars(
            select(LedgerBlockRecord)
            .where(LedgerBlockRecord.batch_id == batch_id)
            .order_by(LedgerBlockRecord.index.asc())
        ).all()
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No ledger blocks found for batch '{batch_id}'.",
            )
        return [_to_out(row) for row in rows]

    def _fail(
        self,
        rows: list[LedgerBlockRecord],
        failed_index: int,
        detail: str,
    ) -> ChainIntegrityOut:
        broken = [row.index for row in rows if row.index >= failed_index]
        return ChainIntegrityOut(
            valid=False,
            checked_blocks=len(rows),
            failed_index=failed_index,
            detail=detail,
            broken_indexes=broken,
        )

    def verify_integrity(self, session: Session) -> ChainIntegrityOut:
        rows = session.scalars(
            select(LedgerBlockRecord).order_by(LedgerBlockRecord.index.asc())
        ).all()
        if not rows:
            return ChainIntegrityOut(
                valid=True,
                checked_blocks=0,
                failed_index=None,
                detail="Chain is empty.",
            )

        expected_previous = GENESIS_PREVIOUS_HASH
        for row in rows:
            recomputed = compute_block_hash(row.payload_json)
            if row.previous_hash != expected_previous:
                return self._fail(
                    rows,
                    row.index,
                    f"Block {row.index} previous_hash does not match the prior block hash.",
                )
            if row.block_hash != recomputed:
                return self._fail(
                    rows,
                    row.index,
                    f"Block {row.index} hash does not match its payload.",
                )
            payload = json.loads(row.payload_json)
            if payload.get("previous_hash") != row.previous_hash:
                return self._fail(
                    rows,
                    row.index,
                    f"Block {row.index} payload previous_hash mismatch.",
                )
            batch = session.scalars(
                select(BatchRecord)
                .options(selectinload(BatchRecord.harvests))
                .where(BatchRecord.batch_id == row.batch_id)
            ).first()
            if batch is not None:
                live_payload = _canonical_payload(batch, row.previous_hash)
                live_hash = compute_block_hash(live_payload)
                if live_hash != row.block_hash:
                    return self._fail(
                        rows,
                        row.index,
                        (
                            f"Block {row.index} ({row.batch_id}): live batch weight "
                            f"{batch.declared_weight_kg} kg no longer matches the "
                            "committed payload. Recomputed hash differs."
                        ),
                    )
            expected_previous = row.block_hash

        return ChainIntegrityOut(
            valid=True,
            checked_blocks=len(rows),
            failed_index=None,
            detail="All block hashes recomputed and linked correctly.",
            broken_indexes=[],
        )

    def run_tamper_test(self, session: Session, *, reset: bool = False) -> TamperTestOut:
        row = session.scalars(select(LedgerBlockRecord).order_by(LedgerBlockRecord.index.asc())).first()
        if row is None:
            raise HTTPException(status_code=409, detail="Ledger is empty. Commit a batch before the tamper test.")
        batch = session.scalars(
            select(BatchRecord)
            .options(selectinload(BatchRecord.harvests))
            .where(BatchRecord.batch_id == row.batch_id)
        ).first()
        if batch is None:
            raise HTTPException(status_code=404, detail=f"Batch '{row.batch_id}' is missing.")
        payload = json.loads(row.payload_json)
        committed = float(payload["declared_weight_kg"])
        if reset:
            batch.declared_weight_kg = committed
            session.flush()
            integrity = self.verify_integrity(session)
            return TamperTestOut(
                action="reset",
                batch_id=batch.batch_id,
                stored_weight_kg=batch.declared_weight_kg,
                committed_weight_kg=committed,
                integrity=integrity,
                note="Restored declared_weight_kg from the committed payload. Hash-chain should verify again.",
            )
        batch.declared_weight_kg = round(committed + 3.5, 3)
        session.flush()
        integrity = self.verify_integrity(session)
        return TamperTestOut(
            action="tamper",
            batch_id=batch.batch_id,
            stored_weight_kg=batch.declared_weight_kg,
            committed_weight_kg=committed,
            integrity=integrity,
            note=(
                "Changed batches.declared_weight_kg in the database, bypassing commit. "
                "Integrity recomputes the hash from the live batch row."
            ),
        )

    def live_batch_verified(self, session: Session, batch_id: str) -> tuple[bool, str]:
        integrity = self.verify_integrity(session)
        if not integrity.valid:
            return False, integrity.detail
        try:
            self.get_custody(session, batch_id)
        except HTTPException:
            return False, f"Batch '{batch_id}' is not on the ledger."
        return True, integrity.detail


ledger_service = LedgerService()
