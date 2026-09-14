from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.database import get_db

router = APIRouter(tags=["health"])

SPA_INDEX = Path(__file__).resolve().parents[2] / "web" / "dist" / "index.html"


@router.get("/")
def root():
    if SPA_INDEX.is_file():
        return FileResponse(SPA_INDEX)
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
