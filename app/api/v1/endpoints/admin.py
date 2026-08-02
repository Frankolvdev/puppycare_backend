from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.device import AdminCreateDeviceRequest, DeviceResponse
from app.services.admin_device_service import (
    create_device_from_backoffice,
    get_devices_for_backoffice,
)
from app.services.qr_service import generate_device_qr_png

router = APIRouter()


@router.post(
    "/devices",
    response_model=DeviceResponse,
    summary="Create device from backoffice",
)
def create_device(
    payload: AdminCreateDeviceRequest,
    db: Session = Depends(get_db),
):
    # Create a physical device from the backoffice.
    return create_device_from_backoffice(
        db=db,
        payload=payload,
    )


@router.get(
    "/devices",
    response_model=list[DeviceResponse],
    summary="List devices from backoffice",
)
def list_devices(
    db: Session = Depends(get_db),
):
    # List all physical devices for the backoffice.
    return get_devices_for_backoffice(db=db)


@router.get(
    "/devices/{device_id}/qr",
    summary="Generate device QR code",
)
def get_device_qr(
    device_id: str,
):
    # Generate QR PNG containing the device_id.
    png_bytes = generate_device_qr_png(device_id)

    return Response(
        content=png_bytes,
        media_type="image/png",
    )