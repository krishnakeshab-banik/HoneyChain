from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database import get_db

router = APIRouter(tags=["health"])


@router.get("/")
def root() -> dict[str, str]:
    return {
        "project": "HoneyChain",
        "version": "0.1.0",
        "status": "running",
        "message": "HoneyChain backend is alive.",
    }


@router.get("/health")
def health_check(session: Session = Depends(get_db)) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "healthy"}
