from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.deps import get_current_user
from backend.models.user import UserRecord
from backend.services import assistant_service, gemini_service

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=800)
    language: str = "en"


class ObserveRequest(BaseModel):
    image_base64: str = Field(..., min_length=20)
    mime_type: str = "image/jpeg"
    language: str = "en"


@router.post("/ask")
def ask(
    payload: AskRequest,
    session: Session = Depends(get_db),
    user: UserRecord = Depends(get_current_user),
) -> dict:
    context = assistant_service.user_context(session, user)
    answer, ai_used, label, language = gemini_service.answer_grounded(
        payload.question, payload.language, context
    )
    return {
        "answer": answer,
        "ai_used": ai_used,
        "ai_label": label,
        "language": language,
    }


@router.post("/observe")
def observe(
    payload: ObserveRequest,
    user: UserRecord = Depends(get_current_user),
) -> dict:
    del user
    text, used = gemini_service.observe_image(payload.image_base64, payload.mime_type, payload.language)
    return {
        "observation": text,
        "ai_used": used,
        "ai_label": (
            "Preliminary AI observation of the photo — not a diagnosis. "
            "Talk to your KVIC officer if you are worried about the colony."
        ),
    }
