from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import UserRecord
from backend.services.auth_service import decode_token, load_user
from backend.services.me_service import assert_hive_access, hives_for_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login-form", auto_error=False)


def get_optional_user(
    token: str | None = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> UserRecord | None:
    if not token:
        return None
    username = decode_token(token)
    return load_user(session, username)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    session: Session = Depends(get_db),
) -> UserRecord:
    if not token:
        raise HTTPException(status_code=401, detail="Sign in is required for this action.")
    username = decode_token(token)
    return load_user(session, username)


def require_roles(*roles: str):
    def _checker(user: UserRecord = Depends(get_current_user)) -> UserRecord:
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{user.role}' cannot perform this action.",
            )
        return user

    return _checker


def require_hive_access(hive_id: str, user: UserRecord | None, session: Session) -> None:
    if user is None:
        return
    assert_hive_access(session, user, hive_id)


def scoped_hives(session: Session, user: UserRecord | None):
    if user is None:
        from backend.services.hive_service import list_hives

        return list_hives(session)
    return hives_for_user(session, user)
