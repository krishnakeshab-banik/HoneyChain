from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import require_roles
from backend.models.user import UserRecord
from backend.schemas.ledger import ChainIntegrityOut, LedgerBlockOut, TamperTestOut
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


@router.post("/tamper-test", response_model=TamperTestOut)
def run_tamper_test(
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("admin")),
) -> TamperTestOut:
    return ledger_service.run_tamper_test(session, reset=False)


@router.post("/tamper-reset", response_model=TamperTestOut)
def reset_tamper_test(
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("admin")),
) -> TamperTestOut:
    return ledger_service.run_tamper_test(session, reset=True)
