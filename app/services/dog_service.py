from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.app.app_user import AppUser
from app.repositories.dog_repository import (
    create_dog,
    dog_has_active_device,
    get_user_dog,
    list_user_dogs,
    soft_delete_dog,
    update_dog,
)
from app.schemas.dog import CreateDogRequest, UpdateDogRequest


def format_dog_response(db: Session, dog) -> dict:
    # Format dog response for API output.
    return {
        "id": str(dog.id),
        "name": dog.name,
        "breed": dog.breed,
        "age": dog.age,
        "weight_kg": float(dog.weight_kg) if dog.weight_kg is not None else None,
        "photo_url": dog.photo_url,
        "has_device": dog_has_active_device(db, dog.id),
    }


def create_user_dog(db: Session, current_user: AppUser, payload: CreateDogRequest) -> dict:
    # Create a dog profile for the authenticated user.
    dog = create_dog(db=db, owner_id=current_user.id, payload=payload)
    return format_dog_response(db, dog)


def get_user_dogs(db: Session, current_user: AppUser) -> list[dict]:
    # Return all dog profiles owned by the authenticated user.
    dogs = list_user_dogs(db=db, owner_id=current_user.id)
    return [format_dog_response(db, dog) for dog in dogs]


def get_user_dog_by_id(db: Session, current_user: AppUser, dog_id: str) -> dict:
    # Return one dog profile owned by the authenticated user.
    dog = get_user_dog(db=db, owner_id=current_user.id, dog_id=dog_id)

    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found.",
        )

    return format_dog_response(db, dog)


def update_user_dog(db: Session, current_user: AppUser, dog_id: str, payload: UpdateDogRequest) -> dict:
    # Update one dog profile owned by the authenticated user.
    dog = get_user_dog(db=db, owner_id=current_user.id, dog_id=dog_id)

    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found.",
        )

    dog = update_dog(db=db, dog=dog, payload=payload)
    return format_dog_response(db, dog)


def delete_user_dog(db: Session, current_user: AppUser, dog_id: str) -> dict:
    # Soft delete one dog profile and release its active device.
    dog = get_user_dog(db=db, owner_id=current_user.id, dog_id=dog_id)

    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dog not found.",
        )

    soft_delete_dog(db=db, dog=dog)

    return {
        "status": "ok",
        "dog_deleted": True,
    }