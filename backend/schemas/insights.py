from __future__ import annotations

from pydantic import BaseModel


class HealthPrediction(BaseModel):
    hive_id: str
    status: str
    confidence: float
    features: dict[str, float]
    model_name: str
    trained_on: str


class YieldForecast(BaseModel):
    hive_id: str
    predicted_weight_kg: float
    predicted_honey_kg: float | None = None
    horizon_readings: int
    model_name: str
    trained_on: str
    recent_weight_kg: float


class InsightsOut(BaseModel):
    health: HealthPrediction
    forecast: YieldForecast
    computed_explanation: str = ""
    ai_explanation: str | None = None
    ai_available: bool = False
    ai_label: str = (
        "AI-generated explanation of the real sensor data and model output. "
        "The numbers above come from the hive readings and models, not from the assistant."
    )
