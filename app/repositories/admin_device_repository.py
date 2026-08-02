from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.devices.device import Device
from app.schemas.device import AdminCreateDeviceRequest, AdminUpdateDeviceRequest


def get_device_by_device_id(db: Session, device_id: str) -> Device | None:
    """
    Find a device by its public device_id.
    """
    return db.query(Device).filter(Device.device_id == device_id).first()


def create_admin_device(db: Session, payload: AdminCreateDeviceRequest) -> Device:
    """
    Create a device from the backoffice.
    """
    existing_device = get_device_by_device_id(db, payload.device_id)

    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device already exists.",
        )

    device = Device(
        device_id=payload.device_id,
        module=payload.module,
        apn=payload.apn,
        is_active=True,
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


def list_admin_devices(db: Session) -> list[Device]:
    """
    List all registered devices.
    """
    return db.query(Device).order_by(Device.created_at.desc()).all()


def update_admin_device(
    db: Session,
    device_id: str,
    payload: AdminUpdateDeviceRequest,
) -> Device:
    """
    Update a device from the backoffice.
    """
    device = get_device_by_device_id(db=db, device_id=device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    device.module = payload.module
    device.apn = payload.apn
    device.is_active = payload.is_active

    db.commit()
    db.refresh(device)

    return device


def set_admin_device_active(
    db: Session,
    device_id: str,
    is_active: bool,
) -> Device:
    """
    Activate or deactivate a device.
    """
    device = get_device_by_device_id(db=db, device_id=device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found.",
        )

    device.is_active = is_active

    db.commit()
    db.refresh(device)

    return device