"""Build a hive-level training table from the inspected local MSPB files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "mspb"
OUT = DATA / "training_table.csv"


def hive_id_to_tag(value) -> int | None:
    digits = "".join(ch for ch in str(value).strip() if ch.isdigit())
    if not digits:
        return None
    return int("2" + digits.zfill(5))


def _clean_yard(value) -> str:
    text = str(value or "").strip()
    if "Dubuc" in text:
        return "Dubuc"
    if text.lower().startswith("c") and "t" in text.lower():
        return "Cote"
    return text or "unknown"


def aggregate_sensors(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, usecols=["tag_number", "temperature", "humidity", "audio_density"])
    frame["temperature"] = frame["temperature"].where(frame["temperature"].between(-10, 50))
    frame["humidity"] = frame["humidity"].clip(upper=100)
    grouped = frame.groupby("tag_number").agg(
        mean_temp=("temperature", "mean"),
        std_temp=("temperature", "std"),
        min_temp=("temperature", "min"),
        max_temp=("temperature", "max"),
        mean_humidity=("humidity", "mean"),
        std_humidity=("humidity", "std"),
        min_humidity=("humidity", "min"),
        max_humidity=("humidity", "max"),
        mean_audio_density=("audio_density", "mean"),
        reading_count=("temperature", "count"),
    )
    return grouped.reset_index()


def load_d1_annotations() -> pd.DataFrame:
    raw = pd.read_excel(DATA / "D1_ant.xlsx", sheet_name="Phenotypic measurements", header=None)
    body = raw.iloc[2:].copy()
    body.columns = [f"c{i}" for i in range(raw.shape[1])]
    out = pd.DataFrame(
        {
            "source": "D1",
            "apiary_id": body["c1"].map(_clean_yard),
            "tag_number": body["c3"].map(hive_id_to_tag),
            "capped_brood": pd.to_numeric(body["c4"], errors="coerce"),
            "total_brood": pd.to_numeric(body["c6"], errors="coerce"),
            "varroa_a": pd.to_numeric(body["c8"], errors="coerce"),
            "varroa_b": pd.to_numeric(body["c10"], errors="coerce"),
            "defensive_a": pd.to_numeric(body["c12"], errors="coerce"),
            "hygienic_a": pd.to_numeric(body["c16"], errors="coerce"),
            "hygienic_b": pd.to_numeric(body["c18"], errors="coerce"),
            "honey_kg": pd.to_numeric(body["c20"], errors="coerce"),
            "mortality_cause": pd.NA,
            "weight_nov_kg": pd.NA,
            "weight_apr_kg": pd.NA,
        }
    )
    return out.dropna(subset=["tag_number"])


def load_d2_annotations() -> pd.DataFrame:
    raw = pd.read_excel(DATA / "D2_ant.xlsx")
    out = pd.DataFrame(
        {
            "source": "D2",
            "apiary_id": raw["Apiary"].map(_clean_yard),
            "tag_number": raw["Hive ID"].map(hive_id_to_tag),
            "capped_brood": pd.NA,
            "total_brood": pd.NA,
            "varroa_a": pd.NA,
            "varroa_b": pd.NA,
            "defensive_a": pd.NA,
            "hygienic_a": pd.NA,
            "hygienic_b": pd.NA,
            "honey_kg": pd.NA,
            "mortality_cause": raw["Mortality cause"],
            "weight_nov_kg": pd.to_numeric(raw["weight (kg) Nov 4 2020"], errors="coerce"),
            "weight_apr_kg": pd.to_numeric(raw["weight (kg) Apr 5 2021"], errors="coerce"),
        }
    )
    return out.dropna(subset=["tag_number"])


def _num(value) -> float | None:
    try:
        if value is None or pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def health_label(row: pd.Series) -> str | None:
    varroa_vals = [v for v in (_num(row.get("varroa_a")), _num(row.get("varroa_b"))) if v is not None]
    hyg_vals = [v for v in (_num(row.get("hygienic_a")), _num(row.get("hygienic_b"))) if v is not None]
    honey = _num(row.get("honey_kg"))
    mort = row.get("mortality_cause")
    nov = _num(row.get("weight_nov_kg"))
    apr = _num(row.get("weight_apr_kg"))
    loss = (nov - apr) if nov is not None and apr is not None else None
    if (isinstance(mort, str) and mort.strip()) or honey == 0 or (hyg_vals and min(hyg_vals) < 70):
        return "needs-inspection"
    if (varroa_vals and max(varroa_vals) >= 1.0) or (hyg_vals and min(hyg_vals) < 85) or (loss is not None and loss > 12):
        return "stressed"
    if varroa_vals or hyg_vals or honey is not None or nov is not None:
        return "healthy"
    return None


def _align_for_concat(frame: pd.DataFrame) -> pd.DataFrame:
    numeric = [
        "capped_brood",
        "total_brood",
        "varroa_a",
        "varroa_b",
        "defensive_a",
        "hygienic_a",
        "hygienic_b",
        "honey_kg",
        "weight_nov_kg",
        "weight_apr_kg",
    ]
    out = frame.copy()
    for col in numeric:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["mortality_cause"] = out["mortality_cause"].astype("object")
    return out


def main() -> None:
    d1 = _align_for_concat(
        load_d1_annotations().merge(aggregate_sensors(DATA / "D1_sensor_data.csv"), on="tag_number", how="inner")
    )
    d2 = _align_for_concat(
        load_d2_annotations().merge(aggregate_sensors(DATA / "D2_sensor_data.csv"), on="tag_number", how="inner")
    )
    frame = pd.concat([d1, d2], ignore_index=True, sort=False)
    frame["health_label"] = frame.apply(health_label, axis=1)
    frame.to_csv(OUT, index=False)
    print(f"wrote {OUT} rows={len(frame)} d1={len(d1)} d2={len(d2)}")
    print(frame["health_label"].value_counts(dropna=False).to_string())
    print("yield rows", int(frame["honey_kg"].notna().sum()))


if __name__ == "__main__":
    main()
