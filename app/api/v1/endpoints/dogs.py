from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import time

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.app.app_user import AppUser
from app.models.devices.device import Device
from app.models.devices.device_reading import DeviceReading
from app.models.dogs.dog_breed import DogBreed
from app.models.dogs.dog_device import DogDevice
from app.schemas.dog import CreateDogRequest, DogResponse, UpdateDogRequest
from app.services.dog_service import (
    create_user_dog,
    delete_user_dog,
    get_user_dog_by_id,
    get_user_dogs,
    update_user_dog,
)

router = APIRouter()


class LinkDeviceRequest(BaseModel):
    device_id: str


@router.post("/", response_model=DogResponse, summary="Create dog profile")
def create_dog_endpoint(
    payload: CreateDogRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    return create_user_dog(db=db, current_user=current_user, payload=payload)


@router.get("/", response_model=list[DogResponse], summary="List my dogs")
def list_dogs_endpoint(
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    return get_user_dogs(db=db, current_user=current_user)


@router.get("/breeds", summary="List dog breeds")
def list_dog_breeds(db: Session = Depends(get_db)):
    breeds = (
        db.query(DogBreed)
        .filter(DogBreed.is_active == True)
        .order_by(DogBreed.name.asc())
        .all()
    )

    return [
        {
            "id": str(breed.id),
            "name": breed.name,
            "heart_rate_min": breed.heart_rate_min,
            "heart_rate_max": breed.heart_rate_max,
            "temperature_min": breed.temperature_min,
            "temperature_max": breed.temperature_max,
        }
        for breed in breeds
    ]


@router.post("/{dog_id}/link-device", summary="Link device to dog after new reading")
def link_device_to_dog_endpoint(
    dog_id: str,
    payload: LinkDeviceRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    dog = get_user_dog_by_id(db=db, current_user=current_user, dog_id=dog_id)

    device = (
        db.query(Device)
        .filter(Device.device_id == payload.device_id.strip())
        .first()
    )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dispositivo no encontrado.",
        )

    last_reading = (
        db.query(DeviceReading)
        .filter(DeviceReading.device_id == device.id)
        .order_by(DeviceReading.created_at.desc())
        .first()
    )

    baseline_created_at = last_reading.created_at if last_reading else None

    timeout_seconds = 60
    interval_seconds = 3
    started_at = time.time()

    while time.time() - started_at < timeout_seconds:
        db.expire_all()

        latest_reading = (
            db.query(DeviceReading)
            .filter(DeviceReading.device_id == device.id)
            .order_by(DeviceReading.created_at.desc())
            .first()
        )

        has_new_reading = False

        if baseline_created_at is None and latest_reading is not None:
            has_new_reading = True

        if (
            baseline_created_at is not None
            and latest_reading is not None
            and latest_reading.created_at > baseline_created_at
        ):
            has_new_reading = True

        if has_new_reading:
            db.query(DogDevice).filter(
                DogDevice.dog_id == dog.id,
                DogDevice.is_active == True,
            ).update({"is_active": False})

            db.query(DogDevice).filter(
                DogDevice.device_id == device.id,
                DogDevice.is_active == True,
            ).update({"is_active": False})

            link = DogDevice(
                dog_id=dog.id,
                device_id=device.id,
                is_active=True,
            )

            db.add(link)
            db.commit()

            return {
                "status": "linked",
                "message": "Dispositivo vinculado correctamente.",
                "dog_id": str(dog.id),
                "device_id": device.device_id,
                "reading_id": str(latest_reading.id),
            }

        time.sleep(interval_seconds)

    raise HTTPException(
        status_code=status.HTTP_408_REQUEST_TIMEOUT,
        detail="No se detectó actividad nueva del dispositivo. Mantén el dispositivo encendido y conectado a internet.",
    )


@router.get("/{dog_id}/latest-reading", summary="Get latest dog reading")
def get_latest_dog_reading_endpoint(
    dog_id: str,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    dog = get_user_dog_by_id(db=db, current_user=current_user, dog_id=dog_id)

    active_link = (
        db.query(DogDevice)
        .filter(DogDevice.dog_id == dog.id, DogDevice.is_active == True)
        .first()
    )

    if not active_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog has no active device.",
        )

    reading = (
        db.query(DeviceReading)
        .filter(DeviceReading.device_id == active_link.device_id)
        .order_by(DeviceReading.created_at.desc())
        .first()
    )

    if not reading:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No readings found.",
        )

    return {
        "id": str(reading.id),
        "device_id": str(reading.device_id),
        "dog_temperature": reading.dog_temperature,
        "ambient_temperature": reading.ambient_temperature,
        "pulse_raw": reading.pulse_raw,
        "heart_bpm": reading.heart_bpm,
        "battery": reading.battery,
        "gps_lat": reading.gps_lat,
        "gps_lon": reading.gps_lon,
        "created_at": reading.created_at,
    }


@router.get("/{dog_id}", response_model=DogResponse, summary="Get dog profile")
def get_dog_endpoint(
    dog_id: str,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    return get_user_dog_by_id(db=db, current_user=current_user, dog_id=dog_id)


@router.put("/{dog_id}", response_model=DogResponse, summary="Update dog profile")
def update_dog_endpoint(
    dog_id: str,
    payload: UpdateDogRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    return update_user_dog(
        db=db,
        current_user=current_user,
        dog_id=dog_id,
        payload=payload,
    )


@router.delete("/{dog_id}", summary="Delete dog profile")
def delete_dog_endpoint(
    dog_id: str,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    return delete_user_dog(db=db, current_user=current_user, dog_id=dog_id)