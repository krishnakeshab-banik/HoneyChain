"""Server-side Gemini calls. Numbers are never taken from the model."""

from __future__ import annotations

import logging
import os
import re

import httpx

from backend.schemas.insights import HealthPrediction, YieldForecast

logger = logging.getLogger("honeychain")

GEMINI_MODELS = (
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
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

FALLBACK_LEAD = {
    "en": "Here is what HoneyChain can tell you from live records and the product itself. If a figure is not listed, it is not available yet.",
    "hi": "HoneyChain आपके लाइव रिकॉर्ड और उत्पाद ज्ञान से यह बता सकता है। जो आँकड़ा सूची में नहीं है, वह अभी उपलब्ध नहीं है।",
    "bn": "HoneyChain আপনার লাইভ রেকর্ড ও পণ্যের তথ্য থেকে এটি বলতে পারে। তালিকায় নেই এমন কোনো সংখ্যা এখন নেই।",
    "ta": "HoneyChain உங்கள் நேரடி பதிவுகள் மற்றும் தயாரிப்பு விளக்கத்திலிருந்து இதைச் சொல்லும். பட்டியலில் இல்லாத எண் இன்னும் இல்லை.",
    "kn": "HoneyChain ನಿಮ್ಮ ಲೈವ್ ದಾಖಲೆಗಳು ಮತ್ತು ಉತ್ಪನ್ನದಿಂದ ಇದನ್ನು ಹೇಳುತ್ತದೆ. ಪಟ್ಟಿಯಲ್ಲಿ ಇಲ್ಲದ ಅಂಕಿ ಇನ್ನೂ ಲಭ್ಯವಿಲ್ಲ.",
    "te": "HoneyChain మీ లైవ్ రికార్డులు మరియు ఉత్పత్తి సమాచారం నుండి ఇది చెబుతుంది. జాబితాలో లేని సంఖ్య ఇంకా అందుబాటులో లేదు.",
    "mr": "HoneyChain तुमच्या लाइव्ह नोंदी आणि उत्पादनातून हे सांगू शकते. यादीत नसलेली आकडेवारी अजून उपलब्ध नाही.",
}

REFUSE = {
    "en": "I can only help with HoneyChain — hives, harvests, batches, lab, ledger, QR verify, market, insights, and how to use this app.",
    "hi": "मैं केवल HoneyChain में मदद कर सकता हूँ — छत्ते, फसल, बैच, लैब, लेजर, QR जाँच, बाज़ार, इनसाइट्स, और इस ऐप का उपयोग।",
    "bn": "আমি শুধু HoneyChain নিয়ে সাহায্য করি — ছাঁক, ফসল, ব্যাচ, ল্যাব, লেজার, QR, বাজার, ইনসাইটস এবং অ্যাপ ব্যবহার।",
    "ta": "நான் HoneyChain மட்டுமே உதவுவேன் — தேனீக்கூடு, அறுவடை, தொகுதி, ஆய்வகம், லெட்ஜர், QR, சந்தை, நுண்ணறிவு, செயலி பயன்பாடு.",
    "kn": "ನಾನು HoneyChain ಬಗ್ಗೆ ಮಾತ್ರ ಸಹಾಯ ಮಾಡುತ್ತೇನೆ — ಜೇನುಗೂಡು, ಸುಗ್ಗಿ, ಬ್ಯಾಚ್, ಲ್ಯಾಬ್, ಲೆಡ್ಜರ್, QR, ಮಾರುಕಟ್ಟೆ, ಒಳನೋಟ, ಅಪ್ಲಿಕೇಶನ್.",
    "te": "నేను HoneyChain గురించి మాత్రమే సహాయం చేస్తాను — తేనెటీగల పెట్టె, పంట, బ్యాచ్, ల్యాబ్, లెడ్జర్, QR, మార్కెట్, ఇన్‌సైట్స్, యాప్.",
    "mr": "मी फक्त HoneyChain मध्ये मदत करतो — पोळी, कापणी, बॅच, लॅब, लेजर, QR, बाजार, इनसाइट्स आणि अॅप वापर.",
}


def api_key() -> str:
    return (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()


def detect_language(text: str, hinted: str = "en") -> str:
    hinted = (hinted or "en")[:2]
    if any("\u0b80" <= ch <= "\u0bff" for ch in text):
        return "ta"
    if any("\u0c00" <= ch <= "\u0c7f" for ch in text):
        return "te"
    if any("\u0c80" <= ch <= "\u0cff" for ch in text):
        return "kn"
    if any("\u0980" <= ch <= "\u09ff" for ch in text):
        return "bn"
    if any("\u0900" <= ch <= "\u097f" for ch in text):
        return "mr" if hinted == "mr" else "hi"
    return hinted if hinted in LANG_NAMES else "en"


def computed_explanation(health: HealthPrediction, forecast: YieldForecast) -> str:
    feats = health.features
    text = (
        f"This hive's live readings give a colony status of {health.status} "
        f"(model confidence {(health.confidence * 100):.1f}%). "
        f"{health.status_meaning or ''} "
        f"Mean inside temperature {feats.get('mean_inside_temp', 0):.1f} °C, "
        f"mean humidity {feats.get('mean_humidity', 0):.1f}%, "
        f"weight change {feats.get('weight_slope', 0):.2f} kg in the recent window. "
        f"Latest measured hive weight {forecast.recent_weight_kg:.2f} kg; "
        f"short-horizon forecast {forecast.predicted_weight_kg:.2f} kg. "
    )
    if health.reasons:
        text += "Why: " + " ".join(health.reasons[:4]) + " "
    if forecast.predicted_honey_kg is not None:
        text += (
            f"Seasonal honey-yield estimate from the MSPB temperature/humidity model "
            f"is {forecast.predicted_honey_kg:.2f} kg (not the hive scale). "
        )
    text += "These figures are recomputed from the current sensor history each time you open this page."
    return text


def _generate(prompt: str, timeout: float = 20.0) -> str | None:
    key = api_key()
    if not key:
        logger.warning("Assistant: GEMINI_API_KEY is not set.")
        return None
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    last_status = None
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=timeout)
            last_status = response.status_code
            if response.status_code >= 400:
                logger.warning("Assistant: model %s returned HTTP %s", model, response.status_code)
                continue
            data = response.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            text = "".join(item.get("text", "") for item in parts).strip()
            if text:
                return text
        except Exception:
            logger.warning("Assistant: model %s request failed", model, exc_info=False)
            continue
    logger.warning("Assistant: no Gemini model returned text (last HTTP %s)", last_status)
    return None


def explain_insights(health: HealthPrediction, forecast: YieldForecast, language: str = "en") -> tuple[str | None, bool]:
    facts = computed_explanation(health, forecast)
    lang = LANG_NAMES.get(language, "English")
    prompt = (
        f"Write 2 short sentences in {lang} explaining these already-computed hive facts "
        "for a beekeeper. Do not invent extra numbers. Do not diagnose disease with certainty. "
        "Say what the status means and which live readings pushed it that way. "
        "If humidity is high and weight gain is low, you may mention possible colony stress as a possibility only.\n\n"
        f"FACTS:\n{facts}"
    )
    text = _generate(prompt)
    return text, bool(api_key()) and text is not None


def answer_grounded(question: str, language: str, context: str) -> tuple[str, bool, str, str]:
    lang = detect_language(question, language)
    lang_name = LANG_NAMES.get(lang, "English")
    prompt = (
        f"You are HoneyChain, a working assistant inside the HoneyChain honey-traceability app. "
        f"Reply entirely in {lang_name}. Be concise and practical.\n"
        "You MAY answer any question about this product: roles (beekeeper, officer, lab, admin, consumer), "
        "login, harvest logging, lab inspection, oracle 10% weight check, ledger hash-chain, QR / consumer verify, "
        "CloneWatch, Market Linkage, insights/models, guided tour, languages, and this user's own live records.\n"
        "Use the CONTEXT for this user's numbers. Never invent statistics. "
        "If a number is missing from context, say it is not yet available.\n"
        "If asked for another person's private data, refuse.\n"
        "If the question is unrelated to HoneyChain, beekeeping, or this app, refuse politely in the same language.\n\n"
        f"CONTEXT:\n{context}\n\nQUESTION:\n{question}"
    )
    text = _generate(prompt)
    if text:
        return text, True, "Answered in your language from HoneyChain records and product knowledge.", lang
    fallback = _fallback_answer(question, context, lang)
    return fallback, False, "Answered from your live HoneyChain records.", lang


def observe_image(image_b64: str, mime: str, language: str = "en") -> tuple[str, bool]:
    key = api_key()
    lang = LANG_NAMES.get(language, "English")
    if not key:
        return (
            "Photo observation needs GEMINI_API_KEY on the server. "
            "This is never a diagnosis — ask your KVIC officer if you are worried about the colony.",
            False,
        )
    prompt = (
        f"Describe what you see on this hive/comb photo in {lang} in 2 sentences. "
        "This is a preliminary observation only, not a veterinary diagnosis. "
        "Do not invent sensor numbers. Tell the beekeeper to consult a KVIC officer for concerns."
    )
    text = _generate_image(prompt, image_b64, mime)
    if text:
        return text, True
    return ("Could not read the photo. Sensor numbers on this page are unchanged.", False)


def _generate_image(prompt: str, image_b64: str, mime: str) -> str | None:
    key = api_key()
    if not key:
        return None
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime, "data": image_b64}},
                ]
            }
        ]
    }
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=20.0)
            if response.status_code >= 400:
                continue
            data = response.json()
            parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            text = "".join(item.get("text", "") for item in parts).strip()
            if text:
                return text
        except Exception:
            continue
    return None


_PRODUCT_RE = re.compile(
    r"hive|harvest|batch|honey|weight|humidity|market|ledger|qr|tour|login|colony|"
    r"insight|alert|verify|oracle|lab|officer|beekeeper|package|clone|trace|"
    r"how|what|help|hello|hi|namaste|namaskar",
    re.I,
)
_OFF_TOPIC_RE = re.compile(r"cricket|world cup|bitcoin|lottery|movie", re.I)


def _fallback_answer(question: str, context: str, language: str = "en") -> str:
    lang = language if language in FALLBACK_LEAD else "en"
    indic = lang != "en"
    if _OFF_TOPIC_RE.search(question) and not _PRODUCT_RE.search(question):
        return REFUSE[lang]
    if not indic and not _PRODUCT_RE.search(question):
        return REFUSE[lang]
    return f"{FALLBACK_LEAD[lang]}\n\n{context}"
