from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.package import PackageCreate, PackageOut
from backend.services import package_service

router = APIRouter(prefix="/api", tags=["packages"])


@router.get("/packages", response_model=list[PackageOut])
def get_packages(session: Session = Depends(get_db)) -> list[PackageOut]:
    return package_service.list_packages(session)


@router.post("/packages", response_model=PackageOut, status_code=201)
def create_package(
    payload: PackageCreate,
    session: Session = Depends(get_db),
) -> PackageOut:
    return package_service.create_package(session, payload)


@router.get("/packages/{package_id}", response_model=PackageOut)
def get_package(package_id: str, session: Session = Depends(get_db)) -> PackageOut:
    return package_service.get_package(session, package_id)


@router.delete("/packages/{package_id}", status_code=204)
def delete_package(package_id: str, session: Session = Depends(get_db)) -> Response:
    package_service.delete_package(session, package_id)
    return Response(status_code=204)


@router.get("/packages/{package_id}/qr")
def get_package_qr(package_id: str, session: Session = Depends(get_db)) -> FileResponse:
    package = package_service.get_package(session, package_id)
    path = Path(package.qr_image_path)
    if not path.is_file():
        raise HTTPException(status_code=404, detail="QR image file is missing.")
    return FileResponse(path, media_type="image/png", filename=f"{package_id}.png")
