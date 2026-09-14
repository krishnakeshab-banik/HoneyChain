"""Colony health classifier and yield models.

Health and seasonal honey-kg models are trained on the inspected local MSPB
D1/D2 table (`ml/data/mspb/SCHEMA.md`). Live inference uses only
temperature/humidity summaries that exist on HoneyChain sensors — MSPB audio
is not required. `predicted_weight_kg` is a short-horizon fit on this hive's
own scale readings, never MSPB honey kilograms.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sqlalchemy.orm import Session

from backend.schemas.insights import HealthPrediction, InsightsOut, YieldForecast
from backend.schemas.telemetry import SensorReading
from backend.services import gemini_service
from backend.services.sensor_service import require_enough_readings

REPO = Path(__file__).resolve().parents[2]
ART = REPO / "ml" / "artifacts"
TABLE = REPO / "ml" / "data" / "mspb" / "training_table.csv"

MSPB_FEATURES = [
    "mean_temp",
    "std_temp",
    "min_temp",
    "max_temp",
    "mean_humidity",
    "std_humidity",
    "min_humidity",
    "max_humidity",
]
MIN_READINGS = 5
HEALTH_TRAINED_ON = (
    "MSPB local D1/D2 files (inspected schema in ml/data/mspb/SCHEMA.md). "
    "Health labels are conservative inspection-risk rules from varroa, hygienic %, "
    "honey=0, and winter mortality/weight loss — not a veterinary diagnosis. "
    "Live features are this hive's temperature and humidity summaries only."
)
YIELD_TRAINED_ON = (
    "Seasonal honey kg: LinearRegression on MSPB D1 Total honey production "
    "using temperature/humidity summaries (see SCHEMA.md). "
    "predicted_weight_kg is a separate LinearRegression on this hive's recent "
    "scale readings — not MSPB honey."
)


def _live_features(readings: list[SensorReading]) -> dict[str, float]:
    temps = np.array([item.inside_temperature_c for item in readings], dtype=float)
    hums = np.array([item.humidity_pct for item in readings], dtype=float)
    weights = np.array([item.weight_kg for item in readings], dtype=float)
    outsides = np.array([item.outside_temperature_c for item in readings], dtype=float)
    return {
        "mean_inside_temp": float(temps.mean()),
        "std_inside_temp": float(temps.std()),
        "mean_humidity": float(hums.mean()),
        "std_humidity": float(hums.std()),
        "mean_weight": float(weights.mean()),
        "weight_slope": float(weights[-1] - weights[0]),
        "mean_outside_temp": float(outsides.mean()),
        "mean_temp": float(temps.mean()),
        "std_temp": float(temps.std(ddof=1)) if len(temps) > 1 else 0.0,
        "min_temp": float(temps.min()),
        "max_temp": float(temps.max()),
        "min_humidity": float(hums.min()),
        "max_humidity": float(hums.max()),
    }


STATUS_MEANING = {
    "healthy": (
        "Inspection-risk looks low from this hive's temperature and humidity pattern. "
        "That is not a veterinary all-clear — it is the model's coarse risk class."
    ),
    "stressed": (
        "The classifier sees climate patterns that, in training, lined up with colony stress "
        "(varroa load, weak hygiene, or winter weight loss). It cannot name a disease from these sensors."
    ),
    "needs-inspection": (
        "The classifier recommends a physical inspection. Training labels used winter mortality, "
        "zero honey, or poor hygiene — not a pathogen ID from live IoT."
    ),
}


def _class_probabilities(model, vector: np.ndarray) -> dict[str, float]:
    if not hasattr(model, "predict_proba"):
        return {}
    proba = model.predict_proba(vector)[0]
    classes = list(model.classes_)
    return {str(name): round(float(value), 4) for name, value in zip(classes, proba)}


def _live_reasons(features: dict[str, float], status: str) -> list[str]:
    reasons: list[str] = []
    temp = features.get("mean_inside_temp") or features.get("mean_temp") or 0.0
    humidity = features.get("mean_humidity") or 0.0
    slope = features.get("weight_slope") or 0.0
    if temp < 32:
        reasons.append(
            f"Mean inside temperature is {temp:.1f} °C, cooler than a typical brood nest (32–36 °C)."
        )
    elif temp > 36.5:
        reasons.append(
            f"Mean inside temperature is {temp:.1f} °C, warmer than a typical brood nest (32–36 °C)."
        )
    else:
        reasons.append(f"Mean inside temperature is {temp:.1f} °C, inside the usual brood-nest band.")
    if humidity >= 80:
        reasons.append(f"Mean humidity is high at {humidity:.1f}%, which can stress a colony.")
    elif humidity <= 40:
        reasons.append(f"Mean humidity is low at {humidity:.1f}%.")
    else:
        reasons.append(f"Mean humidity is {humidity:.1f}%.")
    if slope <= -0.4:
        reasons.append(f"Hive weight fell {abs(slope):.2f} kg across the recent window.")
    elif slope >= 0.4:
        reasons.append(f"Hive weight rose {slope:.2f} kg across the recent window.")
    else:
        reasons.append(f"Hive weight was nearly steady ({slope:.2f} kg change).")
    reasons.append(STATUS_MEANING.get(status, "Status is an inspection-risk class, not a disease name."))
    reasons.append(
        "Held-out health accuracy is 40% — treat this as a hint to look at the colony, not a diagnosis."
    )
    return reasons


def _feature_drivers(model, features: dict[str, float]) -> list:
    from backend.schemas.insights import FeatureDriver

    importances = {}
    if hasattr(model, "feature_importances_"):
        importances = {name: float(value) for name, value in zip(MSPB_FEATURES, model.feature_importances_)}
    typical = {
        "mean_temp": (34.0, "°C"),
        "std_temp": (0.8, "°C"),
        "min_temp": (31.0, "°C"),
        "max_temp": (36.5, "°C"),
        "mean_humidity": (65.0, "%"),
        "std_humidity": (4.0, "%"),
        "min_humidity": (50.0, "%"),
        "max_humidity": (85.0, "%"),
    }
    ranked = sorted(MSPB_FEATURES, key=lambda name: importances.get(name, 0.0), reverse=True)
    drivers = []
    for name in ranked[:4]:
        value = float(features.get(name, 0.0))
        center, unit = typical.get(name, (0.0, ""))
        delta = value - center
        vs = "near typical" if abs(delta) < (2.0 if "humidity" in name or "temp" in name else 0.5) else (
            "higher" if delta > 0 else "lower"
        )
        drivers.append(
            FeatureDriver(
                feature=name,
                value=round(value, 3),
                importance=round(importances.get(name, 0.0), 4),
                vs_typical=vs,
                note=f"{value:.2f} {unit} vs typical ~{center:.1f} {unit} ({vs}).",
            )
        )
    return drivers


def _mspb_vector(features: dict[str, float]) -> np.ndarray:
    return np.array([features[name] for name in MSPB_FEATURES], dtype=float).reshape(1, -1)


def _short_horizon_weight(readings: list[SensorReading]) -> float:
    weights = np.array([item.weight_kg for item in readings], dtype=float)
    steps = np.arange(len(weights), dtype=float).reshape(-1, 1)
    model = LinearRegression()
    model.fit(steps, weights)
    return float(model.predict([[len(weights) + 7]])[0])


def _fit_from_table() -> tuple[RandomForestClassifier, LinearRegression]:
    if not TABLE.exists():
        raise RuntimeError(
            f"Missing {TABLE}. Place the four local MSPB files in ml/data/mspb/ "
            "and run: python ml/prepare_mspb.py && python ml/train_mspb.py"
        )
    frame = pd.read_csv(TABLE)
    health = frame.dropna(subset=MSPB_FEATURES + ["health_label"])
    yield_rows = frame.dropna(subset=MSPB_FEATURES + ["honey_kg"])
    clf = RandomForestClassifier(n_estimators=120, random_state=42, class_weight="balanced")
    clf.fit(health[MSPB_FEATURES].to_numpy(), health["health_label"])
    reg = LinearRegression()
    if len(yield_rows) >= 8:
        reg.fit(yield_rows[MSPB_FEATURES].to_numpy(), yield_rows["honey_kg"])
    ART.mkdir(parents=True, exist_ok=True)
    payload = {"features": MSPB_FEATURES, "trained_on": HEALTH_TRAINED_ON}
    joblib.dump({**payload, "model": clf}, ART / "mspb_health.joblib")
    joblib.dump({**payload, "model": reg, "trained_on": YIELD_TRAINED_ON}, ART / "mspb_yield.joblib")
    return clf, reg


def _load_bundle(path: Path):
    bundle = joblib.load(path)
    if isinstance(bundle, dict) and "model" in bundle:
        return bundle["model"]
    return bundle


class MLService:
    def __init__(self) -> None:
        self.health_model: RandomForestClassifier | None = None
        self.yield_model: LinearRegression | None = None
        self._fitted = False

    def fit(self) -> None:
        health_path = ART / "mspb_health.joblib"
        yield_path = ART / "mspb_yield.joblib"
        if health_path.exists() and yield_path.exists():
            self.health_model = _load_bundle(health_path)
            self.yield_model = _load_bundle(yield_path)
        else:
            self.health_model, self.yield_model = _fit_from_table()
        self._fitted = True

    def _ensure_fit(self) -> None:
        if not self._fitted:
            self.fit()

    def predict_health(self, readings: list[SensorReading]) -> HealthPrediction:
        self._ensure_fit()
        features = _live_features(readings)
        vector = _mspb_vector(features)
        label = str(self.health_model.predict(vector)[0])
        proba = self._class_probs(vector)
        confidence = float(proba.get(label, 0.0))
        return HealthPrediction(
            hive_id=readings[0].hive_id,
            status=label,
            confidence=round(confidence, 4),
            features=features,
            model_name="RandomForestClassifier",
            trained_on=HEALTH_TRAINED_ON,
            class_probabilities=proba,
            reasons=_live_reasons(features, label),
            drivers=_feature_drivers(self.health_model, features),
            status_meaning=STATUS_MEANING.get(label, ""),
        )

    def _class_probs(self, vector: np.ndarray) -> dict[str, float]:
        return _class_probabilities(self.health_model, vector)

    def predict_yield(self, readings: list[SensorReading]) -> YieldForecast:
        self._ensure_fit()
        features = _live_features(readings)
        predicted_weight = _short_horizon_weight(readings)
        honey = None
        if self.yield_model is not None and hasattr(self.yield_model, "coef_"):
            honey = float(self.yield_model.predict(_mspb_vector(features))[0])
            honey = round(max(0.0, min(honey, 80.0)), 3)
        return YieldForecast(
            hive_id=readings[0].hive_id,
            predicted_weight_kg=round(predicted_weight, 3),
            predicted_honey_kg=honey,
            horizon_readings=8,
            model_name="LinearRegression",
            trained_on=YIELD_TRAINED_ON,
            recent_weight_kg=readings[-1].weight_kg,
        )

    def insights_for_hive(
        self,
        session: Session,
        hive_id: str,
        *,
        language: str = "en",
        attach_ai: bool = True,
    ) -> InsightsOut:
        readings = require_enough_readings(session, hive_id, MIN_READINGS)
        health = self.predict_health(readings)
        forecast = self.predict_yield(readings)
        computed = gemini_service.computed_explanation(health, forecast)
        ai_text = None
        available = False
        if attach_ai:
            ai_text, available = gemini_service.explain_insights(health, forecast, language)
        return InsightsOut(
            health=health,
            forecast=forecast,
            computed_explanation=computed,
            ai_explanation=ai_text,
            ai_available=available,
        )


ml_service = MLService()
ml_service.fit()
