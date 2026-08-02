from sqlalchemy.orm import Session

from app.repositories.admin_device_repository import (
    create_admin_device,
    list_admin_devices,
    set_admin_device_active,
    update_admin_device,
)
from app.schemas.device import AdminCreateDeviceRequest, AdminUpdateDeviceRequest


def format_device(device) -> dict:
    """
    Format a device for API and template responses.
    """
    return {
        "id": str(device.id),
        "device_id": device.device_id,
        "module": device.module,
        "apn": device.apn,
        "is_active": device.is_active,
    }


def create_device_from_backoffice(
    db: Session,
    payload: AdminCreateDeviceRequest,
) -> dict:
    """
    Create a new physical device from the backoffice.
    """
    device = create_admin_device(db=db, payload=payload)
    return format_device(device)


def get_devices_for_backoffice(db: Session) -> list[dict]:
    """
    Return all registered devices for the backoffice.
    """
    devices = list_admin_devices(db=db)
    return [format_device(device) for device in devices]


def update_device_from_backoffice(
    db: Session,
    device_id: str,
    payload: AdminUpdateDeviceRequest,
) -> dict:
    """
    Update a device from the backoffice.
    """
    device = update_admin_device(
        db=db,
        device_id=device_id,
        payload=payload,
    )

    return format_device(device)


def deactivate_device_from_backoffice(
    db: Session,
    device_id: str,
) -> dict:
    """
    Deactivate a device from the backoffice.
    """
    device = set_admin_device_active(
        db=db,
        device_id=device_id,
        is_active=False,
    )

    return format_device(device)


def activate_device_from_backoffice(
    db: Session,
    device_id: str,
) -> dict:
    """
    Activate a device from the backoffice.
    """
    device = set_admin_device_active(
        db=db,
        device_id=device_id,
        is_active=True,
    )

    return format_device(device)