# HoneyChain

Smart-hive telemetry, harvest-to-package traceability, a local SHA-256 hash-chain, QR consumer verification, CloneWatch anomaly flags, and two scikit-learn models.

This is a hackathon prototype. Several layers are **real application logic**. The system ships with a **one-time synthetic seed** so the first boot is not an empty shell. After that, every new reading, harvest, batch, scan, and model inference is live-computed. The ledger is **not** a public blockchain.

**Primary UI:** React (`web/`) on port 5173 locally. FastAPI (`backend/`) on port 8000. In production, FastAPI also serves the built React app.

**Hosted demo**

| Surface | URL |
| --- | --- |
| Full app (API + UI) | https://honeychain-y8j6.onrender.com |
| Frontend only (proxies `/api` to Render) | https://honey-chain-coral.vercel.app |

Prefer the Render URL for judging: QR codes, verify, and login all stay on one host. The first Render load after idle can take ~30–60 seconds.

## What you can demo

1. **Harvest → lab → oracle → new QR → live verify** — a brand-new package ID (not only `PK-LIVE`) verifies on Consumer Verify.
2. **Lab desk** — pending drafts appear in the queue; **Record lab result** is enabled; commit is blocked until a pass.
3. **Market Linkage** — live listings and one-time seed/example listings are visually separate.
4. **Model card** — honest held-out colony-health accuracy **40.0%** (not a dressed-up number).
5. **Guided tour** — beekeeper (6 steps) and officer (5 steps) run start → Finish; steps are read aloud in the selected language (Hindi included).
6. **Ask HoneyChain** — answers in the language of the question (en / hi / bn / ta / kn / te / mr) from live records and product knowledge. Full conversational AI needs `GEMINI_API_KEY` on the server.
7. **PK-LIVE** and other previously verified flows still work after the above.

## Setup

Python **3.11** from the repository root. Render uses 3.11.9. `numpy` is pinned to **2.4.6** (3.11 wheels; 2.5.x needs Python 3.12).

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Frontend:

```powershell
cd web
npm install
```

Copy `.env.example` to `.env` and fill secrets. Never commit `.env`.

| Variable | Required | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | For Ask / photo observation | Google AI Studio key. Strip spaces. Same value on Render. |
| `HONEYCHAIN_JWT_SECRET` | Production | JWT signing. Generate on Render; do not use the local default. |
| `HONEYCHAIN_PUBLIC_ORIGIN` | Production QR | e.g. `https://honeychain-y8j6.onrender.com` so scanned codes are not localhost. Render also uses `RENDER_EXTERNAL_URL` when set. |
| `CORS_ORIGINS` | If UI is on another host | Comma-separated origins, e.g. `https://honey-chain-coral.vercel.app` |
| `HONEYCHAIN_DATABASE_URL` | Optional | Defaults to SQLite `honeychain.db` in the repo root. |
| `HONEYCHAIN_SKIP_DEMO_SEED` | Tests | Set to `1` so pytest does not load the day-one story. |
| `PYTHON_VERSION` | Render | `3.11.9` |

## Run locally

Three terminals, all from the repository root.

**1. Backend**

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

**2. Simulator** (live hive numbers)

```powershell
python simulator/hive_simulator.py
```

**3. React UI**

```powershell
cd web
npm run dev
```

- API: http://127.0.0.1:8000  
- Docs: http://127.0.0.1:8000/docs  
- React UI: http://127.0.0.1:5173 (`/api` is proxied to the backend)

Streamlit (`python -m streamlit run frontend/app.py`) is an internal leftover. Beekeepers, officers, lab, and consumers use the React app.

## Demo accounts

Seeded on first backend start. Beekeepers use **Sign in** (`/login`). Officers, lab, and admin can also use one-click desks on **Staff** (`/staff`).

| Role | Username | Password | Landing |
| --- | --- | --- | --- |
| Beekeeper | `beekeeper` | `Beekeeper123!` | Own hive `IN-WB-001`, harvests, insights, market |
| Cluster / KVIC officer | `officer` | `Officer123!` | West Bengal cluster, Batch Review, ledger, CloneWatch |
| Lab inspector | `lab` | `Lab123!` | Lab desk: moisture / purity on **pending** drafts |
| KVIC admin | `admin` | `Admin123!` | Full system, tamper-test, users, model card |
| Consumer | *(none)* | — | Home + **Verify your honey**. No login. |

Beekeeper self-registration, password reset, and staff-account creation exist as screens but are **not** a judging path — use the seeded accounts.

JWT access tokens expire in 15 minutes and rotate via `/api/auth/refresh`. Role-scoped reads: a beekeeper token cannot read hive `DE-001`.

### Sitemap

| Path | Who |
| --- | --- |
| `/` `/how-it-works` `/model` `/verify` `/market` `/staff` `/login` `/register` `/forgot-password` `/reset-password` | Public |
| `/app/dashboard` `/app/harvests` `/app/monitor` `/app/insights` `/app/market` `/app/report` | Beekeeper |
| `/app/cluster` `/app/batches` `/app/alerts` `/app/ledger` `/app/clonewatch` | Officer |
| `/app/lab` | Lab |
| `/app/ledger` `/app/clonewatch` `/app/users` `/app/model` `/app/analytics` plus pages above | Admin |

UI strings switch across English, Hindi, Bengali, Tamil, Kannada, Telugu, and Marathi. Batch IDs, hive names, hashes, and dates stay in their original form.

SQLite file: `honeychain.db` in the repo root. A **local** restart does not wipe data. On Render, SQLite is ephemeral (redeploy reseeds).

## Demo journey (judging)

1. Open https://honeychain-y8j6.onrender.com (or local 5173 with backend + simulator). Wait for `/health`.
2. Public home: hive / verified-batch / flagged-scan counts come from `/api/public/stats`.
3. **Verify your honey** with `PK-LIVE` — chain verified, no login.
4. Sign in as `admin`. On **Batch Review**, create a harvest (after the simulator has ticks locally; hosted demo uses seed telemetry).
5. Create a **pending** draft (declared kg within 10% of sensor-logged harvest). Commit before lab must fail.
6. Sign in as `lab`. The draft is in the queue. **Record lab result** = pass.
7. Sign in as `officer` or `admin`. **Run oracle and commit**. A **JUST ISSUED** card shows a new package ID and QR.
8. Open **Consumer Verify** with that new ID (not `PK-LIVE`). Expect **Chain verified**.
9. Scan the QR — it must open the **public** `/verify?package_id=…` URL, not localhost.
10. Verify once in Kolkata and again in Bremen for a CloneWatch distance flag.
11. **Market Linkage**: live board first; Howrah / `DEM-DEMO-WB` only under **Example listings**.
12. **Model**: 40.0% health accuracy, ~17.6 kg honey RMSE — say this out loud; it is a real held-out score.
13. Optional: language → हिन्दी → **Start tour** (beekeeper or officer) through **Finish**.
14. Optional: **Ask** — English and Hindi questions about this hive / harvest / oracle / QR.

## What is simulated vs real

| Piece | Honest status |
| --- | --- |
| Hive sensor values | **Simulated.** `simulator/hive_simulator.py`, `source=simulated`. No live ESP32. |
| DE-001 | **Simulated temperate hive.** Fed by the simulator. |
| Offline/online IoT | **Simulated.** Local online flag + `data/simulator_queue.json`. |
| Harvest / batch / package | **Real app logic** in SQLite. Typed kilograms are demo inputs. |
| Oracle | **Real.** Declared weight within 10% of sensor-logged harvest sum. |
| Ledger | **Real local SHA-256 hash-chain.** Not Fabric or Polygon. |
| QR + consumer passport | **Real.** PNG encodes `{public origin}/verify?package_id=…`. Verify recomputes the ledger and logs a scan. |
| Scan locations | **Simulated** (Kolkata / Mumbai / Bremen). |
| CloneWatch | **Real rules** on those scans. |
| Colony health + yield | **Real scikit-learn** on MSPB D1/D2. Held-out health accuracy **40%** (n=25). Binary collapse scored 52%, still below a 58.8% majority baseline — the 40% figure was kept. |
| Ask HoneyChain | **Gemini** when `GEMINI_API_KEY` is set; otherwise live records + product facts in the question’s language. |
| Ledger tamper-test | **Real.** Admin tampers `declared_weight_kg`; integrity recomputes. **Reset tamper** restores it. |

## Seeded reference data

One-time synthetic seed; later activity is live. Skip with `HONEYCHAIN_SKIP_DEMO_SEED=1` (tests do this).

| ID | What |
| --- | --- |
| `IN-WB-001` | West Bengal demo hive |
| `DE-001` | Bremen demo hive |
| `IN-WB-002` `IN-WB-003` `IN-KA-001` | Extra cluster hives |
| `BK-WB-01` | Ananya Roy |
| `BK-DE-01` | Lena Hoffmann |
| `BT-DEMO-01` `BT-DEMO-02` | Oracle-passed batches |
| `PK-LIVE` | Seed package used on Consumer Verify |
| `DEM-DEMO-WB` | One-time example demand (shown in **Example listings**, not the live board) |

```powershell
python -m backend.seed
python -m backend.seed --reset
```

`--reset` refuses if live (non-demo) ledger blocks already exist.

## Deploy

### Render (recommended — one service)

Python 3 web service, **branch `main`**.

- **Build:**  
  `pip install -r requirements.txt && curl -fsSL https://nodejs.org/dist/v20.18.1/node-v20.18.1-linux-x64.tar.xz | tar -xJ && export PATH="$PWD/node-v20.18.1-linux-x64/bin:$PATH" && cd web && npm ci && npm run build`
- **Start:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`  
  Do **not** use `gunicorn your_application.wsgi`.
- **Env:** `PYTHON_VERSION=3.11.9`, `HONEYCHAIN_JWT_SECRET` (generate), `GEMINI_API_KEY`, `HONEYCHAIN_PUBLIC_ORIGIN=https://honeychain-y8j6.onrender.com`
- If pip fails on `numpy==2.5.3`, you are on an old commit — `main` pins `numpy==2.4.6` for 3.11.
- `requirements.txt` must be UTF-8 (not UTF-16).
- SQLite does not persist across Render deploys. The hive simulator does not run there.

`render.yaml` in the repo matches this.

### Vercel (optional frontend)

Root directory `web`, framework **Vite**. `web/vercel.json` rewrites `/api/*` and `/health` to Render and falls other paths back to `index.html` (so refresh on `/login` does not 404).

Do **not** set `VITE_API_URL` if you use those rewrites. On Render, set `CORS_ORIGINS` to the Vercel origin if the browser calls Render directly.

## Tests

```powershell
python -m pytest
```

`tests/test_end_to_end.py` walks telemetry → harvest → oracle → ledger → QR → verify → CloneWatch.

## Known gaps

- Self-registration, password reset, and creating staff accounts are not a live demo path.
- Ask HoneyChain’s full conversational layer needs `GEMINI_API_KEY` on the **server** (Render), not only in local `.env`.
- Colony-health **40%** is a real held-out score. Do not present it as a strong classifier.
- Hosted demo has no running simulator; hive numbers there are seed + whatever was written before the last deploy.

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
- `GET /api/insights/{hive_id}`
- `POST /api/assistant/ask` `POST /api/assistant/observe`
- `POST /api/auth/login` `POST /api/auth/register` `GET /api/auth/me` `PATCH /api/auth/me/language` `GET /api/auth/me/hives`
- `GET/POST /api/lab/results` `GET /api/lab/queue`
- `GET/POST /api/market/demands` `POST /api/market/demands/{id}/interest` `GET /api/market/prices` `POST /api/market/sales`
- `GET /api/public/stats` `GET /api/public/impact` `GET /api/public/market`
- `GET /api/analytics/admin` `GET /api/analytics/seller`
- `GET/POST /api/alerts`
