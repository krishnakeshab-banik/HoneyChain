from __future__ import annotations

from pydantic import BaseModel, Field


SUPPORTED_LANGUAGES = ("en", "hi", "bn", "ta", "kn", "te", "mr")
STAFF_ROLES = ("officer", "lab", "admin", "beekeeper")


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=4, max_length=120)


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    display_name: str
    language: str
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)


class UserOut(BaseModel):
    username: str
    display_name: str
    role: str
    beekeeper_id: str | None
    cluster: str | None
    region: str | None
    language: str
    email: str | None = None
    phone: str | None = None
    active: bool = True


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=8, max_length=120)
    display_name: str = Field(..., min_length=2, max_length=120)
    region: str = Field(default="West Bengal", min_length=2, max_length=100)
    cluster: str = Field(default="", max_length=100)
    email: str = Field(default="", max_length=120)
    phone: str = Field(default="", max_length=40)
    language: str = Field(default="en", min_length=2, max_length=8)


class LanguageUpdate(BaseModel):
    language: str = Field(..., min_length=2, max_length=8)


class ForgotRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)


class ResetRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    code: str = Field(..., min_length=4, max_length=12)
    password: str = Field(..., min_length=8, max_length=120)


class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=8, max_length=120)
    display_name: str = Field(..., min_length=2, max_length=120)
    role: str = Field(..., min_length=3, max_length=32)
    region: str | None = None
    cluster: str | None = None
    email: str | None = None
    phone: str | None = None


class AdminUserUpdate(BaseModel):
    role: str | None = None
    active: bool | None = None
    region: str | None = None
    cluster: str | None = None
    display_name: str | None = None
