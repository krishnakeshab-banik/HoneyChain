# MSPB local files — discovered schema

Inspected from the four files in this folder. Do not treat the paper abstract as the column list.

## Files

| File | Kind | Rows | Notes |
| --- | --- | --- | --- |
| `D1_ant.xlsx` | annotations | multi-sheet (53 colonies) | Summer 2020 phenotypic workbook |
| `D1_sensor_data.csv` | sensors | 960,809 | 2020-04-16 → 2020-11-05 UTC |
| `D2_ant.xlsx` | annotations | 45 rows, one sheet | Winter 2020–2021 outcomes |
| `D2_sensor_data.csv` | sensors | 876,105 | 2020-11-06 → 2021-04-14 UTC |

D1 and D2 are **not** the same annotation schema. They are concatenated only after an explicit column mapping (see below).

## Sensor CSVs (D1 and D2 share the same 30 columns)

`published_at`, `temperature`, `humidity`, `tag_number`, `beehub_name`, `geolocation`, `hive_power`, `lat`, `long`, `date`, `time`, 16 `hz_*` audio bins (122–580 Hz), `audio_density`, `audio_density_ratio`, `density_variation`.

- No missing values in the scanned numeric/audio columns.
- `tag_number` is the hive/sensor key (int, 6 digits).
- `beehub_name`: `nectar-bh121` or `nectar-bh131` (gateway, not the colony).
- `lat`/`long`/`geolocation` are unused (`POINT (0 0)`).
- Temperature looks like **°C** (D1 0.24–46.45; D2 −50.0–36.57). −50 °C is treated as a sensor fault, not a real colony temperature.
- Humidity looks like **%RH** (D1 14.33–90.9; D2 11.92–101.0). Values above 100 are clipped.

There is **no hive-weight time series** in either sensor file.

## Annotation workbooks

### D1_ant.xlsx sheets

- `READ ME` — field definitions. Hive ID rule is written in the file: prepend `2` to the zero-padded five-digit hive ID (`02056` → sensor `202056`).
- `ID lookup table` — Bee Hub, Yard (`Dubuc` / `Côté`), CRSAD ID, Nectar colony number.
- `Visit` — yard visit log (not used for training).
- `Evaluation 1`–`6` — frame counts by box; first row is a sub-header. Hive ID column is sometimes `Hive ID` and sometimes `Hive ID ` (trailing space).
- `Phenotypic measurements` — **two header rows**. After skipping the title row:

  | Logical field | Source | Notes |
  | --- | --- | --- |
  | bee_hub, apiary/yard, crsad_id, hive_id | cols A–D | hive_id stored as `02056` |
  | capped/uncapped/total brood | E–G | cell counts |
  | brood_date | H | Excel serial dates |
  | varroa_per_100_bees (two visits) | I, K | range 0–2.74 |
  | defensive_stings (two visits) | M, O | flag test, 2 min |
  | hygienic_pct (two visits) | Q, S | 53–100% |
  | honey_kg | U | 0–64.4; 46 non-null of 53 |
  | cluster size / weight before winter | V–X | almost entirely empty in D1 |

### D2_ant.xlsx

Single sheet. Columns: `Hive`, `Apiary`, `Mortality cause`, `Hive ID`, `New hive ID Nov 2020`, `weight (kg) Nov 4 2020`, `weight (kg) Apr 5 2021`, `winter syrup consuption (kg)` (typo in source), `Bees frames Oct 20`, `Bees frames Apr 2021`, `status April 5/9/13`, `status Apr 27/28`.

- Hive ID may appear as an integer (`2056`) or zero-padded text (`02056`). Both map to sensor `tag_number` `202056` via the same rule.
- Mortality: 35 NaN, 5 Queen failure, 4 Dead queen, 1 Starved.
- `status Apr 28` is free text (`good at 13h03`, `drone laying queen…`), not a coded enum.

## Join keys (confirmed)

1. Normalize annotation hive ID → sensor `tag_number`: take digits, `zfill(5)`, prepend `2`.
2. Join annotations to **hive-level sensor aggregates** on `tag_number`.
3. Overlap: D1 53/53 hives present in D1 sensors. D2 44/45 present; **`202203` has no D2 sensor rows** (dropped from D2 feature rows).

Daily timestamp join is not required for yield (one honey value per colony per season). Health uses the same seasonal aggregates; that is an assumption, not a claim that varroa was measured on every sensor day.

## Reconciliation before combining D1 + D2

| Topic | D1 | D2 | Rule used |
| --- | --- | --- | --- |
| Annotation shape | multi-sheet phenotypic | one winter sheet | Map to a shared column set; missing fields stay null |
| Hive ID | `02056` text | `2056` int | Same `tag_number` mapping |
| Season | Apr–Nov 2020 | Nov 2020–Apr 2021 | `source=D1` or `D2`; `apiary_id` = yard name when present |
| Honey yield | yes | no | Yield model trains on D1 rows only |
| Winter mortality / weights | empty | yes | Health labels from D2 use these; D1 does not invent them |
| Sensor columns | identical | identical | Same aggregator |

`apiary_id` is the yard (`Dubuc` / `Cote`) when known, else `unknown`. `source` is `D1` or `D2`.

## Label assumptions (not certain diagnoses)

These are conservative training labels, not veterinary calls:

- **needs-inspection**: D2 `Mortality cause` present, or D1 `honey_kg == 0`, or min hygienic % < 70.
- **stressed**: max varroa/100 bees ≥ 1.0, or min hygienic % < 85, or D2 winter weight loss > 12 kg.
- **healthy**: otherwise, when a row has enough annotation signal.

Varroa counts in this file are low (mostly 0). A “disease” model here is **risk / inspection need**, not a pathogen ID.

## Features that can be served live

HoneyChain live telemetry has inside/outside temperature, humidity, and hive weight. MSPB sensors have temperature, humidity, and audio — **no continuous weight**.

Served models therefore train only on temperature/humidity summaries (`mean`, `std`, `min`, `max`). Audio bins are stored on the training table for research but are **not** required at inference. Live hive weight is shown as a separate measured/forecast figure, not substituted for MSPB honey kilograms.

## Live HoneyChain feature map

| Live sensor field | MSPB training feature |
| --- | --- |
| `inside_temperature_c` window mean/std/min/max | `mean_temp` / `std_temp` / `min_temp` / `max_temp` |
| `humidity_pct` window mean/std/min/max | `mean_humidity` / `std_humidity` / `min_humidity` / `max_humidity` |
| `weight_kg` | not used by MSPB models; used only for `predicted_weight_kg` |
| audio (`hz_*`, density) | trained optionally on the table; **never required at serve time** |

D1 and D2 can share hive `tag_number`s across seasons. Combined rows keep both, distinguished by `source`.

## Evaluation methodology

`ml/train_mspb.py` uses `train_test_split(test_size=0.25, random_state=42)`, stratified on the health label. The joblib artifacts are fit on the **training** rows only. `ml/artifacts/mspb_metrics.json` is computed on the held-out test rows. The app never displays paper-copied or training-set scores.

## Model-fit notes (not hidden)

Held-out 25% test (n_health=25, n_yield=12): health accuracy 0.40, honey RMSE ~17.6 kg. Climate summaries are a weak proxy for phenotypic labels. The models still ship as specified; treat scores as inspection-risk / coarse yield estimates, not strong predictors.

## How to rebuild

```
python ml/prepare_mspb.py
python ml/train_mspb.py
```

`training_table.csv` is the hive-season table used at serve time if `ml/artifacts/*.joblib` are missing. The raw `*_sensor_data.csv` files stay local and are gitignored.
