# HoneyChain

Smart-hive telemetry, harvest-to-package traceability, a local SHA-256 hash-chain, QR consumer verification, CloneWatch anomaly flags, and two scikit-learn models.

This is a hackathon prototype. Several layers are **real application logic**. The system ships with a **one-time synthetic seed** so the first boot is not an empty shell. After that, every new reading, harvest, batch, scan, and model inference is live-computed. The ledger is **not** a public blockchain.

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

Seeded on first backend start. Beekeepers use **Sign in** (`/login`). Officers, lab, and admin can also use one-click desks on **Admin** / **Staff** (`/staff`).

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
| `/` `/how-it-works` `/model` `/verify` `/market` `/staff` `/login` `/register` `/forgot-password` `/reset-password` | Public |
| `/app/dashboard` `/app/harvests` `/app/monitor` `/app/insights` `/app/market` `/app/report` | Beekeeper |
| `/app/cluster` `/app/batches` `/app/alerts` `/app/ledger` `/app/clonewatch` | Officer |
| `/app/lab` | Lab |
| `/app/ledger` `/app/clonewatch` `/app/users` `/app/model` `/app/analytics` plus the pages above | Admin |
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
| QR + consumer passport | **Real.** A PNG encodes `{origin}/verify?package_id=…`. Opening that URL or `GET /api/verify/{package_id}` runs a live ledger check, shows harvests and declared kg, and logs a scan. Missing PNG files are regenerated on read. |
| Scan locations | **Simulated** (Kolkata / Mumbai / Bremen presets). |
| CloneWatch flags | **Real rules** on those simulated scans: too many scans, implausible distance/time, or an oracle-failed batch. |
| Colony health + yield forecast | **Real scikit-learn models** trained on local MSPB D1/D2 (`ml/data/mspb/SCHEMA.md`). Metrics on **Model** (`/model` public, `/app/model` admin) are a held-out 25% test split — the served models were fit only on the training rows. Live inference uses temperature/humidity only. The health classifier’s honest 3-class accuracy is **40%** (n=25). Collapsing labels to healthy vs needs-attention scored **52%**, which is still below the **58.8%** majority baseline, so the transparency page was not changed. |
| Ledger tamper-test | **Real.** Admin **Tamper with first block** on `/app/ledger` changes `batches.declared_weight_kg` in SQLite. Integrity recomputes the hash from the live batch and flags that block and every later block. **Reset tamper** restores the committed weight. |

## Seeded reference data

The system ships with a **one-time synthetic seed for demo purposes; all subsequent activity is live.**

Reference accounts and two original hives always load (`backend/services/seed_service.py`). The fuller day-one story — extra cluster hives, a short telemetry history, two ledgered batches, a package with a small scan log, and a market listing tied to `BT-DEMO-01` — is applied by `backend/seed/` on first boot unless `HONEYCHAIN_SKIP_DEMO_SEED=1` (tests set this).

| ID | What |
| --- | --- |
| `IN-WB-001` | West Bengal demo hive, humid-subtropical profile |
| `DE-001` | Bremen demo hive, temperate profile |
| `IN-WB-002` `IN-WB-003` `IN-KA-001` | Extra cluster hives for concurrent simulator load |
| `BK-WB-01` | Ananya Roy, West Bengal Producer Cluster |
| `BK-DE-01` | Lena Hoffmann, Bremen Cooperative |
| `BT-DEMO-01` `BT-DEMO-02` | Oracle-passed batches on the real hash-chain |

Reseed (idempotent) or reset the demo story only:

```powershell
python -m backend.seed
python -m backend.seed --reset
```

`--reset` refuses if live (non-demo) ledger blocks already exist, so it cannot silently rewrite a chain a judge just committed.

Seed telemetry uses documented climate ranges and RNG seed `20260914` in `backend/seed/hives.py`. Those rows are initialization, not an ongoing fake live feed. The simulator then emits **new** timestamps.

## Demo journey

1. Start backend, simulator, and the React UI.  
2. Open http://127.0.0.1:5173 — the home page loads live hive / verified-batch / flagged-scan counts from `/api/public/stats`.  
3. Click **Verify your honey** (no login) or sign in as `admin` / `Admin123!`.  
4. On **Traceability**, register a harvest after a few simulator ticks.  
5. On **Batch Review**, create a **pending** draft (declared weight within 10% of the sensor-logged harvest). Sign in as `lab` and **Record lab result** = pass.  
6. Back on **Batch Review**, **Oracle commit**. A new package ID and QR appear on that page. Open **Consumer Verify** with that new ID (not only `PK-LIVE`).  
7. Verify once in Kolkata, then again in Bremen to produce a CloneWatch distance flag.  
8. Commit a second batch with an inflated declared weight to produce an oracle rejection on CloneWatch.  
9. Open **Insights** after five or more readings. Expand **Input feature vector**.  
10. Sign in as `admin` and open **Model** for held-out accuracy/RMSE and feature importance.  
11. On **Ledger Integrity**, run **Tamper with first block**, watch the hash fail, then **Reset tamper**.  
12. On Overview, force the simulator **offline** then **online** (or run `python simulator/demo_offline_sync.py`) to show the queue drain without duplicates.  
13. Sign in as `beekeeper` to express interest on **Market Linkage**. Seed/demo listings sit in a separate **Example listings** panel, not in the live board.  
14. Optional: **Start tour** (beekeeper or officer). Steps highlight the real controls and are read aloud in the selected language (Hindi is wired). Finish both scripts before a judging run if you will show them.

## Known gaps

- Beekeeper self-registration, password reset, and staff-account creation are out of this pass. Demo with the seeded accounts above.
- The Ask HoneyChain panel still needs `GEMINI_API_KEY` for conversational Q&A. Tour narration does **not** — it uses the browser speech engine on the tour script.
- Colony-health 40% accuracy is a real held-out score, not a placeholder. Do not present it as a strong classifier.

## API map

- `GET /` `GET /health`
- `GET/POST /api/hives` `GET /api/hives/{id}`
- `POST /api/sensor-readings` `GET /api/hives/{id}/sensor-readings` `GET /api/hives/{id}/summary`
- `GET /api/beekeepers` harvest CRUD under `/api/harvests`
- batch CRUD plus `POST /api/batches/{id}/commit` and `GET /api/oracle-events`
- package CRUD plus `GET /api/packages/{id}/qr`
- `GET /api/ledger/chain` `GET /api/ledger/batches/{id}` `GET /api/ledger/integrity`
- `POST /api/ledger/tamper-test` `POST /api/ledger/tamper-reset` (admin)
- `GET /api/ml/transparency` (admin) `GET /api/public/model`
- `GET /api/demo/status` `POST /api/demo/link` (admin)
- `GET/POST /api/verify/{package_id}`
- `GET /api/clonewatch`
- `GET /api/insights/{hive_id}` (live model output plus an optional Gemini explanation)
- `POST /api/assistant/ask` `POST /api/assistant/observe` (server-side Gemini; set `GEMINI_API_KEY`)
- `POST /api/auth/login` `POST /api/auth/register` `GET /api/auth/me` `PATCH /api/auth/me/language` `GET /api/auth/me/hives`
- `GET/POST /api/lab/results` `GET /api/lab/queue`
- `GET/POST /api/market/demands` `POST /api/market/demands/{id}/interest` `GET /api/market/prices` `POST /api/market/sales`
- `GET /api/public/stats` `GET /api/public/impact` `GET /api/public/market`
- `GET /api/analytics/admin` (admin map, graphs, written report)
- `GET /api/analytics/seller` (beekeeper harvest/sale report)
- `GET/POST /api/alerts`
