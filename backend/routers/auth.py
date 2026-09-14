from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user, require_roles
from backend.models.user import UserRecord
from backend.schemas.auth import (
    ForgotRequest,
    LanguageUpdate,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetRequest,
    TokenOut,
    UserOut,
)
from backend.schemas.telemetry import Hive
from backend.services import auth_service, me_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterRequest, session: Session = Depends(get_db)) -> TokenOut:
    return auth_service.register_beekeeper(session, payload)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginRequest, session: Session = Depends(get_db)) -> TokenOut:
    return auth_service.authenticate(session, payload.username, payload.password)


@router.post("/login-form", response_model=TokenOut)
def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db),
) -> TokenOut:
    return auth_service.authenticate(session, form.username, form.password)


@router.post("/refresh", response_model=TokenOut)
def refresh(payload: RefreshRequest, session: Session = Depends(get_db)) -> TokenOut:
    return auth_service.refresh_tokens(session, payload.refresh_token)


@router.post("/logout")
def logout(payload: RefreshRequest, session: Session = Depends(get_db)) -> dict[str, str]:
    auth_service.revoke_refresh(session, payload.refresh_token)
    return {"status": "signed_out"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotRequest, session: Session = Depends(get_db)) -> dict[str, str]:
    return auth_service.request_password_reset(session, payload.username)


@router.post("/reset-password")
def reset_password(payload: ResetRequest, session: Session = Depends(get_db)) -> dict[str, str]:
    return auth_service.reset_password(session, payload.username, payload.code, payload.password)


@router.get("/me", response_model=UserOut)
def me(user: UserRecord = Depends(get_current_user)) -> UserOut:
    return auth_service.user_out(user)


@router.get("/me/harvests")
def my_harvests(
    user: UserRecord = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict]:
    return me_service.harvests_for_user(session, user)


@router.get("/me/cluster")
def my_cluster(
    user: UserRecord = Depends(require_roles("officer", "admin")),
    session: Session = Depends(get_db),
) -> dict:
    return me_service.cluster_overview(session, user)


@router.patch("/me/language", response_model=UserOut)
def set_language(
    payload: LanguageUpdate,
    user: UserRecord = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> UserOut:
    return auth_service.set_language(session, user, payload.language)


@router.get("/me/hives", response_model=list[Hive])
def my_hives(
    user: UserRecord = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[Hive]:
    return me_service.hives_for_user(session, user)
