"""Train MSPB health and honey-yield models from the prepared table."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score

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
    "Health labels are conservative inspection-risk rules from varroa, hygienic %, "
    "honey=0, and winter mortality/weight loss — not a veterinary diagnosis. "
    "Yield target is D1 Total honey production (kg)."
)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    if not TABLE.exists():
        raise SystemExit(f"Missing {TABLE}. Run python ml/prepare_mspb.py first.")
    frame = pd.read_csv(TABLE)
    health = frame.dropna(subset=FEATURES + ["health_label"])
    yield_rows = frame.dropna(subset=FEATURES + ["honey_kg"])
    clf = RandomForestClassifier(n_estimators=120, random_state=42, class_weight="balanced")
    Xh = health[FEATURES]
    yh = health["health_label"]
    clf.fit(Xh.to_numpy(), yh)
    acc = None
    min_class = int(yh.value_counts().min()) if len(yh) else 0
    folds = min(5, min_class)
    if len(health) >= 10 and folds >= 2:
        acc = float(cross_val_score(clf, Xh.to_numpy(), yh, cv=folds).mean())
    joblib.dump({"model": clf, "features": FEATURES, "trained_on": TRAINED_ON}, ART / "mspb_health.joblib")

    reg = LinearRegression()
    if len(yield_rows) >= 8:
        Xy = yield_rows[FEATURES]
        yy = yield_rows["honey_kg"]
        reg.fit(Xy.to_numpy(), yy)
        r2 = float(cross_val_score(reg, Xy.to_numpy(), yy, cv=5, scoring="r2").mean()) if len(yield_rows) >= 10 else None
    else:
        r2 = None
    joblib.dump({"model": reg, "features": FEATURES, "trained_on": TRAINED_ON}, ART / "mspb_yield.joblib")
    print(f"health rows={len(health)} labels=\n{yh.value_counts().to_string()}")
    print(f"health cv_acc={acc}")
    print(f"yield rows={len(yield_rows)} cv_r2={r2}")
    print(f"wrote {ART}")


if __name__ == "__main__":
    main()
