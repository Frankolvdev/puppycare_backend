from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.app.app_user import AppUser
from app.repositories.device_repository import (
    create_device_reading,
    create_dog_device_link,
    get_active_link_by_device_id,
    get_active_link_by_dog_id,
    get_device_by_device_id,
)
from app.repositories.dog_repository import get_user_dog
from app.schemas.device import DeviceReadingRequest, LinkDeviceRequest


def save_device_reading(db: Session, payload: DeviceReadingRequest) -> dict:
    """
    Save a telemetry reading sent by a physical device.
    """
    create_device_reading(db=db, payload=payload)

    return {
        "status": "ok",
        "device_id": payload.device_id,
        "reading_saved": True,
    }


def link_device_to_dog(
    db: Session,
    current_user: AppUser,
    payload: LinkDeviceRequest,
) -> dict:
    """
    Link one physical device to one dog profile.
    """
    dog = get_user_dog(
        db=db,
        owner_id=current_user.id,
        dog_id=payload.dog_id,
    )

    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found.",
        )

    device = get_device_by_device_id(
        db=db,
        device_id=payload.device_id,
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    if not device.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device is inactive.",
        )

    existing_dog_link = get_active_link_by_dog_id(db=db, dog_id=dog.id)

    if existing_dog_link:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Dog already has an active device.",
        )

    existing_device_link = get_active_link_by_device_id(
        db=db,
        device_uuid=device.id,
    )

    if existing_device_link:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device is already linked to another dog.",
        )

    create_dog_device_link(
        db=db,
        dog_id=dog.id,
        device_uuid=device.id,
    )

    return {
        "status": "ok",
        "dog_id": str(dog.id),
        "device_id": device.device_id,
        "linked": True,
    }