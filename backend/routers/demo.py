from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from backend.deps import require_roles
from backend.models.user import UserRecord
from simulator.hive_simulator import _load_queue, read_control, write_control

router = APIRouter(prefix="/api/demo", tags=["demo"])


class LinkModeIn(BaseModel):
    mode: str = Field(..., pattern="^(auto|online|offline)$")


class DemoStatusOut(BaseModel):
    mode: str
    queue_length: int
    note: str


@router.get("/status", response_model=DemoStatusOut)
def demo_status(_user: UserRecord = Depends(require_roles("admin"))) -> DemoStatusOut:
    control = read_control()
    return DemoStatusOut(
        mode=str(control.get("mode") or "auto"),
        queue_length=len(_load_queue()),
        note="Simulator reads data/simulator_control.json each tick. Seeded history is one-time; new ticks are live.",
    )


@router.post("/link", response_model=DemoStatusOut)
def set_link(payload: LinkModeIn, _user: UserRecord = Depends(require_roles("admin"))) -> DemoStatusOut:
    write_control(payload.mode)
    return demo_status(_user)
