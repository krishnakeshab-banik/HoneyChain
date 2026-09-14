# HoneyChain

Smart-hive telemetry, harvest-to-package traceability, a local SHA-256 hash-chain, QR consumer verification, CloneWatch anomaly flags, and two scikit-learn models.

This is a hackathon prototype. Several layers are **real application logic**. Sensor values, scan locations, and the ML training table are **simulated**. The ledger is **not** a public blockchain.

## Setup

Python 3.11+ from the repository root (`HoneyChain/`).

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run commands

Use three terminals, all from the repository root.

**1. Backend**

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**2. Simulator**

```powershell
python simulator/hive_simulator.py
```

**3. React UI (primary)**

```powershell
cd web
npm install
npm run dev
```

The Streamlit app remains available until you no longer need it:

```powershell
python -m streamlit run frontend/app.py
```

- API: http://127.0.0.1:8000  
- Docs: http://127.0.0.1:8000/docs  
- React UI (primary): http://127.0.0.1:5173  
- Streamlit UI (internal/admin leftover): http://127.0.0.1:8501  

The public home page, role login, language switcher, lab desk, and Market Linkage live in the React app. Streamlit is no longer the interface a beekeeper, consumer, or KVIC officer is expected to use.

## Demo accounts

Seeded on first backend start. Use these on **Sign in** (`/login`).

| Role | Username | Password | What you see |
| --- | --- | --- | --- |
| Beekeeper | `beekeeper` | `Beekeeper123!` | Own hive `IN-WB-001`, harvests, insights, market interest |
| Cluster / KVIC officer | `officer` | `Officer123!` | West Bengal cluster, harvest review → batches, market demand posts |
| Lab inspector | `lab` | `Lab123!` | Lab desk: moisture/purity on draft batches |
| KVIC admin | `admin` | `Admin123!` | Full dashboards, CloneWatch, alerts, market sales |
| Consumer | *(none)* | — | Home + **Verify your honey**. No login. |

Beekeepers self-register at `/register` (name, phone/email, hive cluster). Officers, lab inspectors, and admins are created only from **User management** by `admin`. The register form has no role picker.

JWT access tokens expire in 15 minutes and rotate via `/api/auth/refresh`. An expired session redirects to `/login?expired=1` and keeps the page you were on. Passwords are bcrypt-hashed (legacy PBKDF2 hashes are still verified and upgraded on login).

Unauthenticated original routes stay public for the simulator and existing tests. **If a JWT is present**, hive/harvest/insight reads are role-scoped: a beekeeper token cannot read `DE-001`. Admin-only APIs (`/api/admin/users`, market demand edits, lab submit) return 403 for the wrong role.

### Sitemap

| Path | Who |
| --- | --- |
| `/` `/how-it-works` `/verify` `/market` `/login` `/register` `/forgot-password` `/reset-password` | Public |
| `/app/dashboard` `/app/harvests` `/app/monitor` `/app/insights` `/app/market` | Beekeeper |
| `/app/cluster` `/app/batches` `/app/alerts` `/app/ledger` `/app/clonewatch` | Officer |
| `/app/lab` | Lab |
| `/app/ledger` `/app/clonewatch` `/app/users` plus the pages above | Admin |
| `/403` `/404` | Error pages |

UI strings switch across English, Hindi, Bengali, Tamil, Kannada, Telugu, and Marathi. Batch IDs, hive names, hashes, and dates stay in their original form.

SQLite file: `honeychain.db` in the repo root. A server restart does **not** wipe readings, harvests, batches, packages, or ledger blocks.

## Tests

```powershell
python -m pytest
```

Every API route has a happy-path and a failure-path test. `tests/test_end_to_end.py` walks telemetry → harvest → oracle → ledger → QR → verify → CloneWatch flag.

## What is simulated vs real

| Piece | Honest status |
| --- | --- |
| Hive sensor values | **Simulated.** `simulator/hive_simulator.py` generates drifted numbers labelled `source=simulated`. There is no live ESP32 and no imported German field dataset. |
| DE-001 | **Simulated temperate hive.** It was previously labelled `real_dataset` without any file behind it. That dead registration is gone. The simulator now feeds DE-001. |
| Offline/online IoT link | **Simulated.** The simulator flips a local online flag and queues readings to `data/simulator_queue.json`. |
| Harvest / batch / package records | **Real application logic** stored in SQLite. The kilograms you type are demo inputs, not a physical extraction. |
| Oracle | **Real logic.** Declared batch weight must stay within 10% of the sum of sensor-corroborated harvest weights. Failures are stored and shown in CloneWatch. |
| Ledger | **Real hash-chain, local only.** `LedgerService` SHA-256s canonical batch JSON plus the previous hash. Integrity is recomputed live. This is not Hyperledger Fabric or Polygon. The class is the swap point for a later chain adapter. |
| QR + consumer passport | **Real.** A PNG is generated per package. `GET /api/verify/{package_id}` and the Streamlit page (`?package_id=`) both run a live ledger check and log a scan. |
| Scan locations | **Simulated** (Kolkata / Mumbai / Bremen presets). |
| CloneWatch flags | **Real rules** on those simulated scans: too many scans, implausible distance/time, or an oracle-failed batch. |
| Colony health + yield forecast | **Real scikit-learn models** (`RandomForestClassifier`, `LinearRegression`) trained on the **local MSPB D1/D2 files** after an inspected schema (`ml/data/mspb/SCHEMA.md`). Live inference uses temperature/humidity only — MSPB audio is not required. `predicted_weight_kg` is this hive's scale; seasonal honey kg is a separate field. |

## Seeded reference data

| ID | What |
| --- | --- |
| `IN-WB-001` | West Bengal demo hive, humid-subtropical profile |
| `DE-001` | Bremen demo hive, temperate profile |
| `BK-WB-01` | Ananya Roy, West Bengal Producer Cluster |
| `BK-DE-01` | Lena Hoffmann, Bremen Cooperative |

## Demo journey

1. Start backend, simulator, and the React UI.  
2. Open http://127.0.0.1:5173 — the home page loads live hive / verified-batch / flagged-scan counts from `/api/public/stats`.  
3. Click **Verify your honey** (no login) or sign in as `admin` / `Admin123!`.  
4. On **Traceability**, register a harvest after a few simulator ticks.  
5. Create a batch whose declared weight matches the harvest (within 10%) and commit it.  
6. Issue a package. Open the QR image or go to **Consumer Verify** with that package ID (or the batch ID).  
7. Verify once in Kolkata, then again in Bremen to produce a CloneWatch distance flag.  
8. Commit a second batch with an inflated declared weight to produce an oracle rejection on CloneWatch.  
9. Open **Insights** after five or more readings.  
10. Sign in as `beekeeper` to express interest on **Market Linkage**, or as `lab` to record moisture/purity on a draft batch.

## API map

- `GET /` `GET /health`
- `GET/POST /api/hives` `GET /api/hives/{id}`
- `POST /api/sensor-readings` `GET /api/hives/{id}/sensor-readings` `GET /api/hives/{id}/summary`
- `GET /api/beekeepers` harvest CRUD under `/api/harvests`
- batch CRUD plus `POST /api/batches/{id}/commit` and `GET /api/oracle-events`
- package CRUD plus `GET /api/packages/{id}/qr`
- `GET /api/ledger/chain` `GET /api/ledger/batches/{id}` `GET /api/ledger/integrity`
- `GET/POST /api/verify/{package_id}`
- `GET /api/clonewatch`
- `GET /api/insights/{hive_id}` (live model output plus an optional Gemini explanation)
- `POST /api/assistant/ask` `POST /api/assistant/observe` (server-side Gemini; set `GEMINI_API_KEY`)
- `POST /api/auth/login` `POST /api/auth/register` `GET /api/auth/me` `PATCH /api/auth/me/language` `GET /api/auth/me/hives`
- `GET/POST /api/lab/results` `GET /api/lab/queue`
- `GET/POST /api/market/demands` `POST /api/market/demands/{id}/interest` `GET /api/market/prices` `POST /api/market/sales`
- `GET /api/public/stats` `GET /api/public/impact`
- `GET/POST /api/alerts`
