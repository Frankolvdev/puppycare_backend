from sqlalchemy.orm import Session

from app.models.devices.device import Device
from app.models.devices.device_reading import DeviceReading
from app.models.dogs.dog_device import DogDevice
from app.schemas.device import DeviceReadingRequest


def normalize_gps_value(value: str | float | None) -> float | None:
    """
    Convert GPS values sent as string, float, or 'null' into float or None.
    """
    if value is None:
        return None

    if isinstance(value, str):
        cleaned_value = value.strip().lower()

        if cleaned_value in ("null", "none", ""):
            return None

        return float(cleaned_value)

    return float(value)


def get_device_by_device_id(db: Session, device_id: str) -> Device | None:
    """
    Find a physical device by its public device_id.
    """
    return db.query(Device).filter(Device.device_id == device_id).first()


def get_or_create_device(db: Session, payload: DeviceReadingRequest) -> Device:
    """
    Get the device by device_id or create it automatically if it does not exist.
    """
    device = get_device_by_device_id(db, payload.device_id)

    if device:
        return device

    device = Device(
        device_id=payload.device_id,
        module=payload.module,
        apn=payload.apn,
        is_active=True,
    )

    db.add(device)
    db.flush()

    return device


def create_device_reading(db: Session, payload: DeviceReadingRequest) -> DeviceReading:
    """
    Store a telemetry reading sent by the physical device.
    """
    device = get_or_create_device(db, payload)

    reading = DeviceReading(
        device_id=device.id,
        internet_connected=payload.internet_connected,
        module=payload.module,
        apn=payload.apn,
        dog_temperature=payload.dog_temperature,
        ambient_temperature=payload.ambient_temperature,
        pulse_raw=payload.pulse_raw,
        heart_bpm=payload.heart_bpm,
        battery=payload.battery,
        gps_lat=normalize_gps_value(payload.gps_lat),
        gps_lon=normalize_gps_value(payload.gps_lon),
    )

    db.add(reading)

    device.module = payload.module
    device.apn = payload.apn

    db.commit()
    db.refresh(reading)

    return reading


def get_active_link_by_dog_id(db: Session, dog_id) -> DogDevice | None:
    """
    Find active device link by dog ID.
    """
    return (
        db.query(DogDevice)
        .filter(
            DogDevice.dog_id == dog_id,
            DogDevice.is_active == True,
        )
        .first()
    )


def get_active_link_by_device_id(db: Session, device_uuid) -> DogDevice | None:
    """
    Find active dog link by internal device UUID.
    """
    return (
        db.query(DogDevice)
        .filter(
            DogDevice.device_id == device_uuid,
            DogDevice.is_active == True,
        )
        .first()
    )


def create_dog_device_link(db: Session, dog_id, device_uuid) -> DogDevice:
    """
    Create an active link between a dog and a physical device.
    """
    link = DogDevice(
        dog_id=dog_id,
        device_id=device_uuid,
        is_active=True,
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link