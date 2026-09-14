from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import require_roles
from backend.models.user import UserRecord
from backend.schemas.auth import AdminUserCreate, AdminUserUpdate, UserOut
from backend.services import auth_service

router = APIRouter(prefix="/api/admin/users", tags=["admin-users"])


@router.get("", response_model=list[UserOut])
def list_users(
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("admin")),
) -> list[UserOut]:
    return auth_service.list_users(session)


@router.post("", response_model=UserOut, status_code=201)
def create_user(
    payload: AdminUserCreate,
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("admin")),
) -> UserOut:
    return auth_service.admin_create_user(session, payload)


@router.patch("/{username}", response_model=UserOut)
def update_user(
    username: str,
    payload: AdminUserUpdate,
    session: Session = Depends(get_db),
    _user: UserRecord = Depends(require_roles("admin")),
) -> UserOut:
    return auth_service.admin_update_user(session, username, payload)
