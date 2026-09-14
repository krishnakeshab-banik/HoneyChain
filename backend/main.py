"""
HoneyChain Backend
==================

FILE:
    backend/main.py

The six original routes keep the same paths and JSON contracts:

    GET  /
    GET  /health
    GET  /api/hives
    POST /api/sensor-readings
    GET  /api/hives/{hive_id}/sensor-readings
    GET  /api/hives/{hive_id}/summary

WHY THIS FILE CHANGED:
    The in-memory hive_store / sensor_store could not survive a process
    restart. Step 0 of the product build requires SQLite persistence
    before any new feature. Route handlers now live in routers/ and
    delegate to services/. Response bodies for the six original routes
    are unchanged.
"""

from __future__ import annotations

import logging
import os
import traceback
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from dotenv import load_dotenv

load_dotenv()

from backend.database import init_db
from backend.routers import (
    alerts,
    analytics,
    assistant,
    auth,
    batches,
    clonewatch,
    demo,
    harvests,
    health,
    hives,
    insights,
    lab,
    ledger,
    market,
    ml,
    packages,
    public,
    sensors,
    users,
    verify,
)

logger = logging.getLogger("honeychain")
SPA_DIR = Path(__file__).resolve().parent.parent / "web" / "dist"


def _cors_origins() -> list[str]:
    origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:8501",
        "http://localhost:8501",
    ]
    extra = os.environ.get("CORS_ORIGINS", "")
    origins.extend(item.strip().rstrip("/") for item in extra.split(",") if item.strip())
    return origins


def _mount_spa(application: FastAPI) -> None:
    if not SPA_DIR.is_dir():
        return
    assets = SPA_DIR / "assets"
    if assets.is_dir():
        application.mount("/assets", StaticFiles(directory=assets), name="spa-assets")

    @application.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        first = full_path.split("/", 1)[0]
        if first in {"docs", "redoc", "openapi.json", "health", "api"}:
            raise HTTPException(status_code=404, detail="Not found.")
        candidate = (SPA_DIR / full_path).resolve()
        if str(candidate).startswith(str(SPA_DIR.resolve())) and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(SPA_DIR / "index.html")


def create_app(*, bootstrap: bool = True) -> FastAPI:
    if bootstrap:
        init_db()

    application = FastAPI(
        title="HoneyChain API",
        description=(
            "Backend API for HoneyChain, "
            "a smart beekeeping and honey traceability platform."
        ),
        version="0.1.0",
    )

    # The React UI on :5173 is a separate origin. Streamlit called the API
    # server-side, so it never needed CORS. This middleware is required so
    # the browser can reach FastAPI without a proxy.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_origin_regex=r"https://.*\.(onrender\.com|vercel\.app)",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application.exception_handler(HTTPException)
    async def http_error(_request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @application.exception_handler(RequestValidationError)
    async def validation_error(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @application.exception_handler(Exception)
    async def internal_error(_request: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled backend error:\n%s", traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error."},
        )

    application.include_router(health.router)
    application.include_router(hives.router)
    application.include_router(sensors.router)
    application.include_router(harvests.router)
    application.include_router(batches.router)
    application.include_router(packages.router)
    application.include_router(ledger.router)
    application.include_router(verify.router)
    application.include_router(clonewatch.router)
    application.include_router(insights.router)
    application.include_router(ml.router)
    application.include_router(assistant.router)
    application.include_router(auth.router)
    application.include_router(lab.router)
    application.include_router(market.router)
    application.include_router(public.router)
    application.include_router(alerts.router)
    application.include_router(analytics.router)
    application.include_router(users.router)
    application.include_router(demo.router)
    _mount_spa(application)
    return application


app = create_app()
