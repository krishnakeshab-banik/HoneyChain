"""One-off inspection of local MSPB files. Not used at runtime."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

SRC = Path(r"C:\Users\godre\Desktop\HoneyChain")


def describe_excel(name: str) -> None:
    path = SRC / name
    xl = pd.ExcelFile(path)
    print(f"\n===== {name} =====")
    print(f"size_bytes={path.stat().st_size} sheets={xl.sheet_names}")
    for sheet in xl.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        print(f"\n--- sheet={sheet!r} rows={len(df)} cols={len(df.columns)} ---")
        print("columns:")
        for col in df.columns:
            series = df[col]
            print(
                f"  {col!r:40} dtype={str(series.dtype):12} "
                f"nulls={int(series.isna().sum())} unique={series.nunique(dropna=True)}"
            )
        print("sample:")
        print(df.head(3).to_string())
        print("numeric describe:")
        num = df.select_dtypes(include="number")
        if not num.empty:
            print(num.describe().T[["min", "max", "mean"]].to_string())


def describe_csv(name: str) -> None:
    path = SRC / name
    print(f"\n===== {name} =====")
    print(f"size_bytes={path.stat().st_size}")
    head = pd.read_csv(path, nrows=8)
    print(f"columns ({len(head.columns)}): {list(head.columns)}")
    print("head dtypes:")
    print(head.dtypes.to_string())
    print(head.head(2).to_string())

    rows = 0
    nulls = None
    tags = set()
    hubs = set()
    tmin = tmax = None
    temp_min = temp_max = None
    hum_min = hum_max = None
    for chunk in pd.read_csv(path, chunksize=80_000):
        rows += len(chunk)
        if nulls is None:
            nulls = chunk.isna().sum()
        else:
            nulls = nulls.add(chunk.isna().sum(), fill_value=0)
        if "tag_number" in chunk.columns:
            tags.update(chunk["tag_number"].dropna().unique().tolist())
        if "beehub_name" in chunk.columns:
            hubs.update(chunk["beehub_name"].dropna().unique().tolist())
        if "published_at" in chunk.columns:
            ts = pd.to_datetime(chunk["published_at"], utc=True, errors="coerce")
            cmin, cmax = ts.min(), ts.max()
            tmin = cmin if tmin is None else min(tmin, cmin)
            tmax = cmax if tmax is None else max(tmax, cmax)
        if "temperature" in chunk.columns:
            temp_min = chunk["temperature"].min() if temp_min is None else min(temp_min, chunk["temperature"].min())
            temp_max = chunk["temperature"].max() if temp_max is None else max(temp_max, chunk["temperature"].max())
        if "humidity" in chunk.columns:
            hum_min = chunk["humidity"].min() if hum_min is None else min(hum_min, chunk["humidity"].min())
            hum_max = chunk["humidity"].max() if hum_max is None else max(hum_max, chunk["humidity"].max())
    print(f"row_count={rows}")
    print(f"published_at range: {tmin} -> {tmax}")
    print(f"temperature range: {temp_min} -> {temp_max}")
    print(f"humidity range: {hum_min} -> {hum_max}")
    print(f"unique tag_number ({len(tags)}): {sorted(tags)[:40]}{'...' if len(tags) > 40 else ''}")
    print(f"unique beehub_name: {sorted(hubs)}")
    print("nulls (top):")
    print(nulls.sort_values(ascending=False).head(12).to_string())


def main() -> None:
    describe_excel("D1_ant.xlsx")
    describe_excel("D2_ant.xlsx")
    describe_csv("D1_sensor_data.csv")
    describe_csv("D2_sensor_data.csv")


if __name__ == "__main__":
    main()
