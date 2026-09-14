from __future__ import annotations

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


def _to_out(record: PackageRecord) -> PackageOut:
    return PackageOut(
        package_id=record.package_id,
        batch_id=record.batch_id,
        qr_reference=record.qr_reference,
        qr_image_path=record.qr_image_path,
        created_at=record.created_at,
    )


def _qr_url(base_url: str, package_id: str) -> str:
    return f"{base_url.rstrip('/')}/?package_id={package_id}"


def _write_qr_png(package_id: str, url: str) -> Path:
    QR_DIR.mkdir(parents=True, exist_ok=True)
    path = QR_DIR / f"{package_id}.png"
    image = qrcode.make(url)
    image.save(path)
    return path


def create_package(session: Session, payload: PackageCreate) -> PackageOut:
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

    qr_reference = _qr_url(payload.verify_base_url, payload.package_id)
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


def list_packages(session: Session) -> list[PackageOut]:
    rows = session.scalars(select(PackageRecord).order_by(PackageRecord.package_id)).all()
    return [_to_out(row) for row in rows]


def get_package(session: Session, package_id: str) -> PackageOut:
    record = session.get(PackageRecord, package_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Package '{package_id}' does not exist.")
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
