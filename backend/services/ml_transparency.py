"""Load held-out MSPB metrics written by ml/train_mspb.py."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import HTTPException

from backend.schemas.ml import (
    FeatureImportance,
    HealthMetrics,
    ModelTransparencyOut,
    PublicModelSummary,
    YieldMetrics,
)

METRICS_PATH = Path(__file__).resolve().parents[2] / "ml" / "artifacts" / "mspb_metrics.json"
NOTE = (
    "Metrics come from a held-out 25% test split. The served models were fit only "
    "on the remaining training rows. These numbers are not copied from a paper."
)


def _load() -> dict:
    if not METRICS_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Model metrics are not on disk yet. An admin should run python ml/train_mspb.py.",
        )
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def transparency() -> ModelTransparencyOut:
    raw = _load()
    health = raw.get("health")
    yield_raw = raw.get("yield")
    return ModelTransparencyOut(
        split=raw.get("split", ""),
        provenance=raw.get("provenance", ""),
        features=raw.get("features", []),
        health=HealthMetrics(**health) if health else None,
        yield_metrics=YieldMetrics(**yield_raw) if yield_raw else None,
        health_feature_importance=[FeatureImportance(**row) for row in raw.get("health_feature_importance", [])],
        yield_feature_importance=[FeatureImportance(**row) for row in raw.get("yield_feature_importance", [])],
        note=NOTE,
    )


def public_summary() -> PublicModelSummary:
    body = transparency()
    return PublicModelSummary(
        health_accuracy=body.health.accuracy if body.health else None,
        health_precision_macro=body.health.precision_macro if body.health else None,
        health_recall_macro=body.health.recall_macro if body.health else None,
        yield_rmse=body.yield_metrics.rmse if body.yield_metrics else None,
        yield_mae=body.yield_metrics.mae if body.yield_metrics else None,
        n_health_test=body.health.n_test if body.health else None,
        n_yield_test=body.yield_metrics.n_test if body.yield_metrics else None,
        provenance=body.provenance,
        split=body.split,
    )
