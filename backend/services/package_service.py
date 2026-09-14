from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import qrcode
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.models.batch import BatchRecord
from backend.models.package import PackageRecord
from backend.schemas.package import PackageCreate, PackageOut

QR_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "qr"
LOCAL_VERIFY = "http://127.0.0.1:5173/verify"


def _to_out(record: PackageRecord) -> PackageOut:
    return PackageOut(
        package_id=record.package_id,
        batch_id=record.batch_id,
        qr_reference=record.qr_reference,
        qr_image_path=record.qr_image_path,
        created_at=record.created_at,
    )


def _is_local_url(url: str) -> bool:
    lowered = (url or "").lower()
    return "127.0.0.1" in lowered or "localhost" in lowered


def public_verify_base(request=None, preferred: str | None = None) -> str:
    """Origin encoded into QR codes. Never prefer localhost when a public host is known."""
    env = (
        os.environ.get("HONEYCHAIN_PUBLIC_ORIGIN")
        or os.environ.get("RENDER_EXTERNAL_URL")
        or ""
    ).strip().rstrip("/")
    if env:
        return f"{env}/verify" if not env.endswith("/verify") else env
    if request is not None:
        host = (request.headers.get("x-forwarded-host") or request.headers.get("host") or "").split(",")[0].strip()
        if host and not _is_local_url(host):
            proto = request.headers.get("x-forwarded-proto") or getattr(request.url, "scheme", None) or "https"
            if "onrender.com" in host or "vercel.app" in host:
                proto = "https"
            return f"{proto}://{host}/verify"
    if preferred and not _is_local_url(preferred):
        return preferred.rstrip("/") if preferred.rstrip("/").endswith("/verify") else f"{preferred.rstrip('/')}/verify"
    return LOCAL_VERIFY


def _qr_url(base_url: str, package_id: str) -> str:
    origin = base_url.rstrip("/")
    if origin.endswith("/verify"):
        return f"{origin}?package_id={package_id}"
    return f"{origin}/verify?package_id={package_id}"


def _write_qr_png(package_id: str, url: str) -> Path:
    QR_DIR.mkdir(parents=True, exist_ok=True)
    path = QR_DIR / f"{package_id}.png"
    image = qrcode.make(url)
    image.save(path)
    return path


def create_package(session: Session, payload: PackageCreate, request=None) -> PackageOut:
    if session.get(PackageRecord, payload.package_id) is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Package '{payload.package_id}' already exists.",
        )
    batch = session.scalars(
        select(BatchRecord).where(BatchRecord.batch_id == payload.batch_id)
    ).first()
    if batch is None:
        raise HTTPException(status_code=404, detail=f"Batch '{payload.batch_id}' does not exist.")
    if batch.status != "committed":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Batch '{payload.batch_id}' is '{batch.status}'. "
                "Only oracle-passed committed batches can be packaged."
            ),
        )

    base = public_verify_base(request, payload.verify_base_url)
    qr_reference = _qr_url(base, payload.package_id)
    qr_path = _write_qr_png(payload.package_id, qr_reference)
    record = PackageRecord(
        package_id=payload.package_id,
        batch_id=payload.batch_id,
        qr_reference=qr_reference,
        qr_image_path=str(qr_path),
        created_at=datetime.now(timezone.utc),
    )
    session.add(record)
    session.flush()
    return _to_out(record)


def list_packages(session: Session, request=None) -> list[PackageOut]:
    rows = session.scalars(select(PackageRecord).order_by(PackageRecord.package_id)).all()
    base = public_verify_base(request)
    out = [_to_out(ensure_qr_file(row, base)) for row in rows]
    session.flush()
    return out


def ensure_qr_file(record: PackageRecord, base_url: str | None = None) -> PackageRecord:
    """Recreate the PNG if missing, and upgrade localhost QR targets to the live origin."""

    base = base_url or LOCAL_VERIFY
    target = _qr_url(base, record.package_id)
    if _is_local_url(target) and record.qr_reference and not _is_local_url(record.qr_reference):
        target = record.qr_reference
    path = Path(record.qr_image_path) if record.qr_image_path else QR_DIR / f"{record.package_id}.png"
    if record.qr_reference != target or not path.is_file():
        written = _write_qr_png(record.package_id, target)
        record.qr_reference = target
        record.qr_image_path = str(written)
    return record


def get_package(session: Session, package_id: str, request=None) -> PackageOut:
    record = session.get(PackageRecord, package_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Package '{package_id}' does not exist.")
    ensure_qr_file(record, public_verify_base(request))
    session.flush()
    return _to_out(record)


def delete_package(session: Session, package_id: str) -> None:
    record = session.get(PackageRecord, package_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Package '{package_id}' does not exist.")
    session.delete(record)
    session.flush()


def load_package_with_batch(session: Session, package_id: str) -> PackageRecord:
    record = session.scalars(
        select(PackageRecord)
        .options(
            selectinload(PackageRecord.batch).selectinload(BatchRecord.harvests),
            selectinload(PackageRecord.scans),
        )
        .where(PackageRecord.package_id == package_id)
    ).first()
    if record is None:
        raise HTTPException(status_code=404, detail=f"Package '{package_id}' does not exist.")
    return record
