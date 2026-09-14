from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.ledger import ChainIntegrityOut, LedgerBlockOut
from backend.services.ledger_service import ledger_service

router = APIRouter(prefix="/api/ledger", tags=["ledger"])


@router.get("/chain", response_model=list[LedgerBlockOut])
def get_chain(session: Session = Depends(get_db)) -> list[LedgerBlockOut]:
    return ledger_service.get_chain(session)


@router.get("/batches/{batch_id}", response_model=list[LedgerBlockOut])
def get_custody(batch_id: str, session: Session = Depends(get_db)) -> list[LedgerBlockOut]:
    return ledger_service.get_custody(session, batch_id)


@router.get("/integrity", response_model=ChainIntegrityOut)
def get_integrity(session: Session = Depends(get_db)) -> ChainIntegrityOut:
    return ledger_service.verify_integrity(session)
