from sqlalchemy.orm import Session

from app.models.dogs.dog import Dog
from app.models.dogs.dog_device import DogDevice
from app.schemas.dog import CreateDogRequest, UpdateDogRequest


def create_dog(db: Session, owner_id, payload: CreateDogRequest) -> Dog:
    # Create a dog profile for an app user.
    dog = Dog(
        owner_id=owner_id,
        name=payload.name,
        breed=payload.breed,
        age=payload.age,
        weight_kg=payload.weight_kg,
        photo_url=payload.photo_url,
        is_deleted=False,
    )

    db.add(dog)
    db.commit()
    db.refresh(dog)

    return dog


def list_user_dogs(db: Session, owner_id) -> list[Dog]:
    # List active dog profiles owned by the user.
    return (
        db.query(Dog)
        .filter(
            Dog.owner_id == owner_id,
            Dog.is_deleted == False,
        )
        .order_by(Dog.created_at.desc())
        .all()
    )


def get_user_dog(db: Session, owner_id, dog_id) -> Dog | None:
    # Get one active dog profile owned by the user.
    return (
        db.query(Dog)
        .filter(
            Dog.id == dog_id,
            Dog.owner_id == owner_id,
            Dog.is_deleted == False,
        )
        .first()
    )


def update_dog(db: Session, dog: Dog, payload: UpdateDogRequest) -> Dog:
    # Update dog profile fields.
    data = payload.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(dog, key, value)

    db.commit()
    db.refresh(dog)

    return dog


def soft_delete_dog(db: Session, dog: Dog) -> Dog:
    # Soft delete dog profile and release active device link.
    dog.is_deleted = True

    active_link = (
        db.query(DogDevice)
        .filter(
            DogDevice.dog_id == dog.id,
            DogDevice.is_active == True,
        )
        .first()
    )

    if active_link:
        active_link.is_active = False

    db.commit()
    db.refresh(dog)

    return dog


def dog_has_active_device(db: Session, dog_id) -> bool:
    # Check if dog has an active device linked.
    return (
        db.query(DogDevice)
        .filter(
            DogDevice.dog_id == dog_id,
            DogDevice.is_active == True,
        )
        .first()
        is not None
    )