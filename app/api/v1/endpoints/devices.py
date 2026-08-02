from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.app.app_user import AppUser
from app.schemas.device import (
    DeviceReadingRequest,
    DeviceReadingResponse,
    LinkDeviceRequest,
    LinkDeviceResponse,
)
from app.services.device_service import (
    link_device_to_dog,
    save_device_reading,
)

router = APIRouter()


@router.post(
    "/readings",
    response_model=DeviceReadingResponse,
    summary="Store device telemetry reading",
)
def create_reading(
    payload: DeviceReadingRequest,
    db: Session = Depends(get_db),
):
    # Store a telemetry reading sent by the physical device.
    return save_device_reading(
        db=db,
        payload=payload,
    )


@router.post(
    "/link",
    response_model=LinkDeviceResponse,
    summary="Link device to dog",
)
def link_device(
    payload: LinkDeviceRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    # Link a physical device to a dog profile owned by the authenticated user.
    return link_device_to_dog(
        db=db,
        current_user=current_user,
        payload=payload,
    )