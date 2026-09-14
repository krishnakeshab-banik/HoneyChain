"""Server-side Gemini calls. Numbers are never taken from the model."""

from __future__ import annotations

import os

import httpx

from backend.schemas.insights import HealthPrediction, YieldForecast

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

LANG_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "kn": "Kannada",
    "te": "Telugu",
    "mr": "Marathi",
}


def api_key() -> str:
    return (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()


def computed_explanation(health: HealthPrediction, forecast: YieldForecast) -> str:
    feats = health.features
    text = (
        f"This hive's live readings give a colony status of {health.status} "
        f"(model confidence {(health.confidence * 100):.1f}%). "
        f"Mean inside temperature {feats.get('mean_inside_temp', 0):.1f} °C, "
        f"mean humidity {feats.get('mean_humidity', 0):.1f}%, "
        f"weight change {feats.get('weight_slope', 0):.2f} kg in the recent window. "
        f"Latest measured hive weight {forecast.recent_weight_kg:.2f} kg; "
        f"short-horizon forecast {forecast.predicted_weight_kg:.2f} kg. "
    )
    if forecast.predicted_honey_kg is not None:
        text += (
            f"Seasonal honey-yield estimate from the MSPB temperature/humidity model "
            f"is {forecast.predicted_honey_kg:.2f} kg (not the hive scale). "
        )
    text += "These figures are recomputed from the current sensor history each time you open this page."
    return text


def _generate(prompt: str, timeout: float = 8.0) -> str | None:
    key = api_key()
    if not key:
        return None
    try:
        response = httpx.post(
            GEMINI_URL,
            params={"key": key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=timeout,
        )
        if response.status_code >= 400:
            return None
        data = response.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = "".join(item.get("text", "") for item in parts).strip()
        return text or None
    except Exception:
        return None


def explain_insights(health: HealthPrediction, forecast: YieldForecast, language: str = "en") -> tuple[str | None, bool]:
    facts = computed_explanation(health, forecast)
    lang = LANG_NAMES.get(language, "English")
    prompt = (
        f"Write 2 short sentences in {lang} explaining these already-computed hive facts "
        "for a beekeeper. Do not invent extra numbers. Do not diagnose disease with certainty. "
        "If humidity is high and weight gain is low, you may mention possible colony stress as a possibility only.\n\n"
        f"FACTS:\n{facts}"
    )
    text = _generate(prompt)
    return text, bool(api_key()) and text is not None


def answer_grounded(question: str, language: str, context: str) -> tuple[str, bool, str]:
    lang = LANG_NAMES.get(language, "English")
    prompt = (
        f"You are the HoneyChain assistant. Reply in {lang}. "
        "Use ONLY the context below plus general beekeeping/product help. "
        "Never invent statistics. If a number is not in the context, say it is not yet available. "
        "If the question is unrelated to HoneyChain, this user's hives, harvests, batches, market, "
        "or basic beekeeping, say plainly that you can only help with HoneyChain. "
        "If asked for another person's data, refuse.\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION:\n{question}"
    )
    text = _generate(prompt)
    if text:
        return text, True, "AI-generated answer grounded in your HoneyChain records."
    fallback = _fallback_answer(question, context)
    return fallback, False, "Plain answer from your live records. The AI service is not available right now."


def observe_image(image_b64: str, mime: str, language: str = "en") -> tuple[str, bool]:
    key = api_key()
    lang = LANG_NAMES.get(language, "English")
    if not key:
        return (
            "Photo observation is not available until an administrator sets GEMINI_API_KEY. "
            "This is never a diagnosis — ask your KVIC officer if you are worried about the colony.",
            False,
        )
    prompt = (
        f"Describe what you see on this hive/comb photo in {lang} in 2 sentences. "
        "This is a preliminary observation only, not a veterinary diagnosis. "
        "Do not invent sensor numbers. Tell the beekeeper to consult a KVIC officer for concerns."
    )
    try:
        response = httpx.post(
            GEMINI_URL,
            params={"key": key},
            json={
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": mime, "data": image_b64}},
                        ]
                    }
                ]
            },
            timeout=12.0,
        )
        if response.status_code >= 400:
            return (
                "Could not read the photo. The colony numbers on this page still come from sensors, not the image.",
                False,
            )
        data = response.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        text = "".join(item.get("text", "") for item in parts).strip()
        return text or "No visual note returned.", bool(text)
    except Exception:
        return ("Could not reach the vision service. Sensor numbers on this page are unchanged.", False)


def _fallback_answer(question: str, context: str) -> str:
    lowered = question.lower()
    terms = (
        "hive",
        "harvest",
        "batch",
        "honey",
        "weight",
        "humidity",
        "market",
        "ledger",
        "qr",
        "tour",
        "login",
        "colony",
        "insight",
        "alert",
        "verify",
    )
    if not any(term in lowered for term in terms) and not any(word in lowered for word in ("help", "how", "what", "hello", "hi")):
        return "I can only help with HoneyChain and your own hives, harvests, and batches. Ask about those, or use Help/Tour."
    return (
        "The AI assistant is not connected, so here is your live record only — no invented numbers.\n\n"
        f"{context}\n\n"
        "If a figure you asked for is not listed, it is not yet available."
    )
