from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas.package import ScanLocationIn, VerifyPassport
from backend.services import clonewatch_service

router = APIRouter(prefix="/api", tags=["verify"])


@router.post("/verify/{package_id}", response_model=VerifyPassport)
def verify_package(
    package_id: str,
    location: ScanLocationIn,
    session: Session = Depends(get_db),
) -> VerifyPassport:
    return clonewatch_service.record_verification(session, package_id, location)


@router.get("/verify/{package_id}", response_model=VerifyPassport)
def verify_package_get(
    package_id: str,
    session: Session = Depends(get_db),
    latitude: float = 22.5726,
    longitude: float = 88.3639,
    location_label: str = "Kolkata shop",
) -> VerifyPassport:
    """Browser-hittable verify URL used by tests and QR deep-links to the API."""

    location = ScanLocationIn(
        latitude=latitude,
        longitude=longitude,
        location_label=location_label,
    )
    return clonewatch_service.record_verification(session, package_id, location)
