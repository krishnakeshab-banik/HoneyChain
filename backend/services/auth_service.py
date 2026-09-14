"""JWT auth with short-lived access tokens and bcrypt password hashes."""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.beekeeper import BeekeeperRecord
from backend.models.refresh import PasswordResetRecord, RefreshTokenRecord
from backend.models.user import UserRecord
from backend.schemas.auth import (
    STAFF_ROLES,
    SUPPORTED_LANGUAGES,
    AdminUserCreate,
    AdminUserUpdate,
    RegisterRequest,
    TokenOut,
    UserOut,
)

JWT_SECRET = os.environ.get("HONEYCHAIN_JWT_SECRET", "honeychain-demo-secret")
JWT_ALG = "HS256"
ACCESS_MINUTES = int(os.environ.get("HONEYCHAIN_ACCESS_MINUTES", "15"))
REFRESH_DAYS = int(os.environ.get("HONEYCHAIN_REFRESH_DAYS", "7"))
PBKDF_ITERATIONS = 120_000


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(password: str, stored: str) -> bool:
    if stored.startswith("$2"):
        return bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))
    try:
        salt_hex, digest_hex = stored.split("$", 1)
    except ValueError:
        return False
    salt = bytes.fromhex(salt_hex)
    expected = bytes.fromhex(digest_hex)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF_ITERATIONS)
    return hmac.compare_digest(actual, expected)


def user_out(record: UserRecord) -> UserOut:
    return UserOut(
        username=record.username,
        display_name=record.display_name,
        role=record.role,
        beekeeper_id=record.beekeeper_id,
        cluster=record.cluster,
        region=record.region,
        language=record.language,
        email=record.email,
        phone=record.phone,
        active=bool(record.active),
    )


def _encode(payload: dict) -> str:
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def create_access_token(record: UserRecord) -> str:
    return _encode(
        {
            "sub": record.username,
            "role": record.role,
            "typ": "access",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_MINUTES),
        }
    )


def issue_refresh_token(session: Session, record: UserRecord) -> str:
    jti = secrets.token_urlsafe(24)
    expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_DAYS)
    session.add(
        RefreshTokenRecord(
            jti=jti,
            username=record.username,
            expires_at=expires,
            revoked=False,
        )
    )
    session.flush()
    return _encode(
        {
            "sub": record.username,
            "typ": "refresh",
            "jti": jti,
            "exp": expires,
        }
    )


def token_bundle(session: Session, record: UserRecord) -> TokenOut:
    return TokenOut(
        access_token=create_access_token(record),
        refresh_token=issue_refresh_token(session, record),
        role=record.role,
        display_name=record.display_name,
        language=record.language,
        expires_in=ACCESS_MINUTES * 60,
    )


def decode_token(token: str, expected_typ: str = "access") -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Your session expired. Sign in again.") from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token.") from exc
    if payload.get("typ") != expected_typ:
        raise HTTPException(status_code=401, detail="Wrong token type.")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload.")
    return str(username)


def decode_refresh(session: Session, token: str) -> UserRecord:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Your session expired. Sign in again.") from exc
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token.") from exc
    if payload.get("typ") != "refresh":
        raise HTTPException(status_code=401, detail="Refresh token required.")
    jti = payload.get("jti")
    username = payload.get("sub")
    stored = session.get(RefreshTokenRecord, jti) if jti else None
    if stored is None or stored.revoked or stored.username != username:
        raise HTTPException(status_code=401, detail="Refresh token is no longer valid.")
    expires = stored.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Your session expired. Sign in again.")
    stored.revoked = True
    session.flush()
    return load_user(session, str(username))


def authenticate(session: Session, username: str, password: str) -> TokenOut:
    record = session.get(UserRecord, username)
    if record is None:
        raise HTTPException(status_code=401, detail="No account found for that username.")
    if not record.active:
        raise HTTPException(status_code=403, detail="This account is not active.")
    if not verify_password(password, record.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password.")
    if not record.password_hash.startswith("$2"):
        record.password_hash = hash_password(password)
        session.flush()
    return token_bundle(session, record)


def refresh_tokens(session: Session, refresh_token: str) -> TokenOut:
    record = decode_refresh(session, refresh_token)
    return token_bundle(session, record)


def revoke_refresh(session: Session, refresh_token: str) -> None:
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALG])
    except jwt.PyJWTError:
        return
    stored = session.get(RefreshTokenRecord, payload.get("jti"))
    if stored is not None:
        stored.revoked = True
        session.flush()


def load_user(session: Session, username: str) -> UserRecord:
    record = session.get(UserRecord, username)
    if record is None:
        raise HTTPException(status_code=401, detail="User no longer exists.")
    if not record.active:
        raise HTTPException(status_code=401, detail="This account has been deactivated.")
    return record


def register_beekeeper(session: Session, payload: RegisterRequest) -> TokenOut:
    if payload.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=422, detail="Unsupported language.")
    if session.get(UserRecord, payload.username) is not None:
        raise HTTPException(status_code=409, detail="That username is already taken.")
    beekeeper_id = f"BK-{payload.username[:12].upper()}"
    cluster = payload.cluster or f"{payload.region} Producer Cluster"
    if session.get(BeekeeperRecord, beekeeper_id) is None:
        session.add(
            BeekeeperRecord(
                beekeeper_id=beekeeper_id,
                name=payload.display_name,
                cluster=cluster,
                region=payload.region,
            )
        )
    session.add(
        UserRecord(
            username=payload.username,
            password_hash=hash_password(payload.password),
            display_name=payload.display_name,
            role="beekeeper",
            beekeeper_id=beekeeper_id,
            cluster=cluster,
            region=payload.region,
            language=payload.language,
            email=payload.email or None,
            phone=payload.phone or None,
            active=True,
        )
    )
    session.flush()
    return authenticate(session, payload.username, payload.password)


def request_password_reset(session: Session, username: str) -> dict[str, str]:
    record = session.get(UserRecord, username)
    if record is None:
        raise HTTPException(status_code=401, detail="No account found for that username.")
    if not record.active:
        raise HTTPException(status_code=403, detail="This account is not active.")
    code = f"{secrets.randbelow(1000000):06d}"
    session.merge(
        PasswordResetRecord(
            username=username,
            code_hash=hash_password(code),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=20),
        )
    )
    session.flush()
    # Demo-only: no email gateway is wired. The code is returned so the
    # forgot-password screen can complete a real reset without SMS/SMTP.
    return {
        "detail": "A reset code was issued for this account.",
        "reset_code": code,
    }


def reset_password(session: Session, username: str, code: str, password: str) -> dict[str, str]:
    stored = session.get(PasswordResetRecord, username)
    if stored is None:
        raise HTTPException(status_code=401, detail="No reset code is waiting for that username.")
    expires = stored.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc) or not verify_password(code, stored.code_hash):
        raise HTTPException(status_code=401, detail="That reset code is invalid or has expired.")
    user = session.get(UserRecord, username)
    if user is None or not user.active:
        raise HTTPException(status_code=401, detail="No account found for that username.")
    user.password_hash = hash_password(password)
    session.delete(stored)
    session.flush()
    return {"detail": "Password updated. You can sign in now."}


def set_language(session: Session, user: UserRecord, language: str) -> UserOut:
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=422, detail="Unsupported language.")
    user.language = language
    session.flush()
    return user_out(user)


def list_users(session: Session) -> list[UserOut]:
    from sqlalchemy import select

    rows = session.scalars(select(UserRecord).order_by(UserRecord.username)).all()
    return [user_out(row) for row in rows]


def admin_create_user(session: Session, payload: AdminUserCreate) -> UserOut:
    if payload.role not in STAFF_ROLES:
        raise HTTPException(status_code=422, detail="Role is not allowed.")
    if session.get(UserRecord, payload.username) is not None:
        raise HTTPException(status_code=409, detail="That username is already taken.")
    beekeeper_id = None
    if payload.role == "beekeeper":
        beekeeper_id = f"BK-{payload.username[:12].upper()}"
        if session.get(BeekeeperRecord, beekeeper_id) is None:
            session.add(
                BeekeeperRecord(
                    beekeeper_id=beekeeper_id,
                    name=payload.display_name,
                    cluster=payload.cluster or f"{payload.region or 'India'} Producer Cluster",
                    region=payload.region or "India",
                )
            )
    record = UserRecord(
        username=payload.username,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
        role=payload.role,
        beekeeper_id=beekeeper_id,
        cluster=payload.cluster,
        region=payload.region,
        language="en",
        email=payload.email,
        phone=payload.phone,
        active=True,
    )
    session.add(record)
    session.flush()
    return user_out(record)


def admin_update_user(session: Session, username: str, payload: AdminUserUpdate) -> UserOut:
    record = session.get(UserRecord, username)
    if record is None:
        raise HTTPException(status_code=404, detail="User does not exist.")
    if payload.role is not None:
        if payload.role not in STAFF_ROLES:
            raise HTTPException(status_code=422, detail="Role is not allowed.")
        record.role = payload.role
    if payload.active is not None:
        record.active = payload.active
    if payload.region is not None:
        record.region = payload.region
    if payload.cluster is not None:
        record.cluster = payload.cluster
    if payload.display_name is not None:
        record.display_name = payload.display_name
    session.flush()
    return user_out(record)
