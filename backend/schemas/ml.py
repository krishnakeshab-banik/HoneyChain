from __future__ import annotations

from pydantic import BaseModel


class FeatureImportance(BaseModel):
    feature: str
    importance: float


class HealthMetrics(BaseModel):
    n_train: int
    n_test: int
    accuracy: float
    precision_macro: float
    recall_macro: float
    per_class: dict[str, dict[str, float]]


class YieldMetrics(BaseModel):
    n_train: int
    n_test: int
    rmse: float
    mae: float


class ModelTransparencyOut(BaseModel):
    split: str
    provenance: str
    features: list[str]
    health: HealthMetrics | None
    yield_metrics: YieldMetrics | None
    health_feature_importance: list[FeatureImportance]
    yield_feature_importance: list[FeatureImportance]
    note: str


class PublicModelSummary(BaseModel):
    health_accuracy: float | None
    health_precision_macro: float | None
    health_recall_macro: float | None
    yield_rmse: float | None
    yield_mae: float | None
    n_health_test: int | None
    n_yield_test: int | None
    provenance: str
    split: str
