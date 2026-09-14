"""Train MSPB models and write held-out evaluation metrics."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent
TABLE = ROOT / "data" / "mspb" / "training_table.csv"
ART = ROOT / "artifacts"
FEATURES = [
    "mean_temp",
    "std_temp",
    "min_temp",
    "max_temp",
    "mean_humidity",
    "std_humidity",
    "min_humidity",
    "max_humidity",
]
TRAINED_ON = (
    "MSPB local D1/D2 files (inspected schema in ml/data/mspb/SCHEMA.md). "
    "International field proxy until an Indian labelled set is available. "
    "Health labels are conservative inspection-risk rules — not a veterinary diagnosis. "
    "The served models are fit on the training split only; metrics are from the held-out test split."
)


def _health_metrics(y_true, y_pred, labels: list[str]) -> dict:
    return {
        "n_test": int(len(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_macro": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "recall_macro": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "per_class": {
            label: {
                "precision": float(precision_score(y_true, y_pred, labels=[label], average="macro", zero_division=0)),
                "recall": float(recall_score(y_true, y_pred, labels=[label], average="macro", zero_division=0)),
            }
            for label in labels
        },
    }


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    if not TABLE.exists():
        raise SystemExit(f"Missing {TABLE}. Run python ml/prepare_mspb.py first.")
    frame = pd.read_csv(TABLE)
    health = frame.dropna(subset=FEATURES + ["health_label"])
    yield_rows = frame.dropna(subset=FEATURES + ["honey_kg"])
    Xh = health[FEATURES]
    yh = health["health_label"]
    Xh_train, Xh_test, yh_train, yh_test = train_test_split(
        Xh, yh, test_size=0.25, random_state=42, stratify=yh
    )
    clf = RandomForestClassifier(n_estimators=120, random_state=42, class_weight="balanced")
    clf.fit(Xh_train.to_numpy(), yh_train)
    health_pred = clf.predict(Xh_test.to_numpy())
    labels = sorted(yh.unique().tolist())
    health_eval = _health_metrics(yh_test, health_pred, labels)
    health_eval["n_train"] = int(len(yh_train))
    health_importance = [
        {"feature": name, "importance": float(value)}
        for name, value in zip(FEATURES, clf.feature_importances_)
    ]
    joblib.dump({"model": clf, "features": FEATURES, "trained_on": TRAINED_ON}, ART / "mspb_health.joblib")

    yield_eval = None
    yield_importance = []
    reg = LinearRegression()
    if len(yield_rows) >= 12:
        Xy = yield_rows[FEATURES]
        yy = yield_rows["honey_kg"]
        Xy_train, Xy_test, yy_train, yy_test = train_test_split(Xy, yy, test_size=0.25, random_state=42)
        reg.fit(Xy_train.to_numpy(), yy_train)
        pred = reg.predict(Xy_test.to_numpy())
        yield_eval = {
            "n_train": int(len(yy_train)),
            "n_test": int(len(yy_test)),
            "rmse": float(np.sqrt(mean_squared_error(yy_test, pred))),
            "mae": float(mean_absolute_error(yy_test, pred)),
        }
        scale = float(np.abs(reg.coef_).sum()) or 1.0
        yield_importance = [
            {"feature": name, "importance": float(abs(coef) / scale)}
            for name, coef in zip(FEATURES, reg.coef_)
        ]
    elif len(yield_rows) >= 8:
        reg.fit(yield_rows[FEATURES].to_numpy(), yield_rows["honey_kg"])
    joblib.dump({"model": reg, "features": FEATURES, "trained_on": TRAINED_ON}, ART / "mspb_yield.joblib")

    metrics = {
        "split": "train_test_split test_size=0.25 random_state=42; health stratified",
        "health": health_eval,
        "yield": yield_eval,
        "health_feature_importance": health_importance,
        "yield_feature_importance": yield_importance,
        "provenance": TRAINED_ON,
        "features": FEATURES,
    }
    (ART / "mspb_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))
    print(f"wrote {ART}")


if __name__ == "__main__":
    main()
