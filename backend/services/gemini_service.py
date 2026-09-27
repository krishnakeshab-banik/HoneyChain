"""Server-side Gemini calls. Numbers are never taken from the model."""

from __future__ import annotations

import logging
import os
import re

import httpx

from backend.schemas.insights import HealthPrediction, YieldForecast

logger = logging.getLogger("honeychain")

# Auth keys (AQ.) are rejected by retired model ids. Current flash models first.
GEMINI_MODELS = (
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemini-2.5-flash",
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


_gemini_blocked = False


def _candidate_text(data: dict) -> str:
    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
    chunks = [item.get("text", "") for item in parts if item.get("text") and not item.get("thought")]
    return "".join(chunks).strip()


def _generate(prompt: str, timeout: float = 12.0) -> str | None:
    return _generate_payload(
        {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"thinkingConfig": {"thinkingLevel": "LOW"}},
        },
        timeout,
    )


def _generate_payload(payload: dict, timeout: float) -> str | None:
    global _gemini_blocked
    key = api_key()
    if not key:
        logger.warning("Assistant: GEMINI_API_KEY is not set.")
        return None
    if _gemini_blocked:
        return None
    headers = {"x-goog-api-key": key, "Content-Type": "application/json"}
    auth_failures = 0
    last_status = None
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=timeout)
        except Exception:
            logger.warning("Assistant: model %s request failed", model, exc_info=False)
            continue
        last_status = response.status_code
        if response.status_code in (401, 403):
            auth_failures += 1
            logger.warning("Assistant: model %s returned HTTP %s", model, response.status_code)
            if auth_failures >= 2:
                _gemini_blocked = True
                return None
            continue
        if response.status_code >= 400:
            logger.warning("Assistant: model %s returned HTTP %s", model, response.status_code)
            continue
        text = _candidate_text(response.json())
        if text:
            return text
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
        f"You are HoneyChain, the assistant inside this honey-traceability app. "
        f"Reply entirely in {lang_name}. Answer the question that was asked, in 2 to 5 sentences.\n"
        "Cover how the product works when asked what this is, what a role does, or how a step works: "
        "beekeeper, KVIC field officer, lab inspector, admin, consumer verify, harvest, lab pass/fail, "
        "the 10% hive-scale weight check, ledger seal, QR, CloneWatch, market, insights, and the guided tour.\n"
        "Use CONTEXT for this user's own numbers. Never invent statistics or another person's private data. "
        "If a number is not in CONTEXT, say it is not available yet.\n"
        "Refuse only when the question is unrelated to honey, beekeeping, or this app.\n\n"
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
    return _generate_payload(
        {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": mime, "data": image_b64}},
                    ],
                }
            ],
            "generationConfig": {"thinkingConfig": {"thinkingLevel": "LOW"}},
        },
        12.0,
    )


_STRONG_RE = re.compile(
    r"hive|harvest|batch|honey|weight|humidity|market|ledger|qr|tour|colony|"
    r"insight|alert|verify|oracle|lab|officer|beekeeper|package|clone|trace|model",
    re.I,
)
_ABOUT_RE = re.compile(r"\b(what|about|this|help|hello|hi|who|how)\b|namaste|namaskar", re.I)
_OFF_TOPIC_RE = re.compile(r"cricket|world cup|bitcoin|lottery|movie|weather|paris|joke|football", re.I)
_HIVE_LINE = re.compile(r"^- ([A-Za-z0-9-]+) \(([^)]+)\): (.+)$", re.M)
_HARVEST_LINE = re.compile(r"^- (HV-\S+) hive (\S+) ([0-9.]+) kg status (\S+)", re.M)

_ABOUT = {
    "beekeeper": (
        "HoneyChain follows your honey from the hive scale to a jar a buyer can check. "
        "You watch your own colonies, log a harvest, and see buyer prices. "
        "An officer groups that harvest into a draft. The lab must pass it. "
        "The batch is sealed only if the claimed kilograms stay within 10% of the hive scale. "
        "The jar then gets a package ID and QR. Anyone can open Verify with no account."
    ),
    "officer": (
        "HoneyChain is the KVIC field record from hive to jar. "
        "You see only your cluster. Group a beekeeper's harvest into a draft batch and leave the lab result pending. "
        "After the lab records a pass, seal the batch only if the claimed kilograms stay within 10% of the hive scale. "
        "That issues a package ID and QR. Ledger Integrity shows whether the seal still matches. "
        "CloneWatch lists jars scanned too often or too far apart."
    ),
    "lab": (
        "HoneyChain is the lab desk for draft honey batches. "
        "You do not create batches and you do not seal them. "
        "Open a waiting batch, enter moisture % and purity %, then pass or fail. "
        "A fail blocks the officer from sealing that batch. A pass unlocks the 10% weight check."
    ),
    "admin": (
        "HoneyChain is the KVIC system of record from hive to jar. "
        "You register hives, create officer and lab accounts, and can run the same draft, lab, and seal steps. "
        "A batch seals only after a lab pass and only if the claimed kilograms stay within 10% of the hive scale. "
        "Ledger Integrity can show a broken chain with Tamper with first block, then Reset tamper. "
        "The model card's colony-health accuracy is about 40% on the held-out test. Map pins are region centers, not live GPS."
    ),
}


def _context_field(context: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}: (.+)$", context, re.M)
    return match.group(1).strip() if match else ""


def _hive_answer(context: str, language: str) -> str:
    hives = _HIVE_LINE.findall(context)
    if not hives:
        lead = "No hives are assigned to this account yet."
        if language == "hi":
            lead = "इस खाते पर अभी कोई छत्ता असाइन नहीं है।"
        return lead
    lines = [f"- {hive_id} ({name}): {detail}" for hive_id, name, detail in hives]
    count = len(hives)
    if language == "hi":
        lead = f"आपको {count} छत्ते दिख रहे हैं।"
    else:
        lead = f"You can see {count} hive." if count == 1 else f"You can see {count} hives."
    return lead + " Colony status and the yield forecast are on the Insights page.\n" + "\n".join(lines)


def _harvest_answer(context: str) -> str:
    summary = _context_field(context, "Harvests visible")
    rows = _HARVEST_LINE.findall(context)
    if not summary and not rows:
        return "No harvests are visible on this account yet."
    lines = [f"- {harvest_id} on {hive_id}: {kg} kg, status {status}" for harvest_id, hive_id, kg, status in rows[:8]]
    body = summary or "Harvests on this account:"
    if lines:
        body += "\n" + "\n".join(lines)
    return body


def _fallback_answer(question: str, context: str, language: str = "en") -> str:
    lang = language if language in FALLBACK_LEAD else "en"
    if _OFF_TOPIC_RE.search(question) and not _STRONG_RE.search(question):
        return REFUSE[lang]
    if lang == "en" and not _STRONG_RE.search(question) and not _ABOUT_RE.search(question):
        return REFUSE[lang]

    role = _context_field(context, "Role") or "beekeeper"
    who = _context_field(context, "Signed-in user")
    q = question.lower()

    def asks(*words: str) -> bool:
        return any(word in q for word in words)

    if asks("hive", "colony", "temperature", "humidity", "weight", "छत्त"):
        text = _hive_answer(context, lang)
    elif asks("harvest", "फसल"):
        text = _harvest_answer(context)
    elif asks("oracle", "10%", "10 percent", "declared"):
        text = (
            "The weight check allows a seal only when the batch's claimed kilograms stay within 10% of the kilograms logged on the hive scale. "
            "Run it on Batch Review after the lab has recorded a pass."
        )
    elif asks("lab", "moisture", "purity", "inspector"):
        text = (
            "The lab desk lists draft batches waiting for inspection. "
            "Enter moisture and purity, then pass or fail. A fail blocks the seal. A pass lets the officer run the 10% weight check."
        )
    elif asks("ledger", "hash", "tamper"):
        text = (
            "Ledger Integrity recalculates the seal every time you open it. "
            "Green means every sealed batch still matches. Red means a stored number was changed. "
            "Only an admin can use Tamper with first block and Reset tamper."
        )
    elif asks("clone", "counterfeit", "fake", "scan"):
        text = "CloneWatch lists jars scanned too many times, scans too far apart to be the same jar, and batches that failed the 10% weight check."
    elif asks("qr", "verify", "package"):
        text = "A sealed batch gets a package ID and QR. Anyone can open Verify and check that ID with no account. The page recomputes the ledger from the live rows."
    elif asks("market", "price", "buyer", "demand"):
        text = "Market Linkage shows standing buyer demand separately from example listings, plus recent verified sale prices."
    elif asks("tour", "walkthrough"):
        text = "Open your name menu and choose Help / Tour. The walkthrough highlights the real controls for your role and reads each step aloud."
    elif asks("model", "accuracy", "insight"):
        text = "The colony-health model card shows about 40% accuracy on the held-out test split. Quote that page rather than a higher number. Live readings for your hives are separate from that score."
    elif asks("who", "role", "login", "sign"):
        text = f"You are signed in as {who or 'this account'}, role {role}."
    else:
        text = _ABOUT.get(role, _ABOUT["beekeeper"])
        if who:
            text = f"You are signed in as {who}, role {role}.\n\n" + text
    if lang == "hi" and not text.startswith("आप"):
        return "HoneyChain आपके रिकॉर्ड से यह बता रहा है।\n\n" + text
    return text
