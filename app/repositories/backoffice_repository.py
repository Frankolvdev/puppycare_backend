from sqlalchemy.orm import Session

from app.models.app.app_user import AppUser
from app.models.devices.device import Device
from app.models.dogs.dog import Dog
from app.models.dogs.dog_device import DogDevice


def list_backoffice_users(db: Session) -> list[AppUser]:
    # Return all app users.
    return db.query(AppUser).order_by(AppUser.created_at.desc()).all()


def get_backoffice_user(db: Session, user_id: str) -> AppUser | None:
    # Return one app user.
    return db.query(AppUser).filter(AppUser.id == user_id).first()


def update_user_backoffice(
    db: Session,
    user_id: str,
    name: str | None,
    email: str | None,
    is_active: bool,
) -> None:
    # Update an app user.
    user = get_backoffice_user(db=db, user_id=user_id)

    if user:
        user.name = name
        user.email = email
        user.is_active = is_active
        db.commit()


def delete_user_permanently(db: Session, user_id: str) -> None:
    # Permanently delete an app user and related records.
    user = get_backoffice_user(db=db, user_id=user_id)

    if user:
        db.delete(user)
        db.commit()


def list_user_dogs_backoffice(db: Session, user_id: str) -> list[Dog]:
    # Return dogs owned by one user.
    return (
        db.query(Dog)
        .filter(
            Dog.owner_id == user_id,
            Dog.is_deleted == False,
        )
        .order_by(Dog.created_at.desc())
        .all()
    )


def list_backoffice_dogs(db: Session) -> list[Dog]:
    # Return all non-deleted dogs.
    return (
        db.query(Dog)
        .filter(Dog.is_deleted == False)
        .order_by(Dog.created_at.desc())
        .all()
    )


def get_backoffice_dog(db: Session, dog_id: str) -> Dog | None:
    # Return one dog.
    return db.query(Dog).filter(Dog.id == dog_id).first()


def create_dog_backoffice(
    db: Session,
    owner_id: str,
    name: str,
    breed_id: str | None,
    age: int | None,
    weight_kg: float | None,
    photo_url: str | None,
) -> None:
    # Create a dog from backoffice.
    dog = Dog(
        owner_id=owner_id,
        name=name,
        breed_id=breed_id or None,
        breed=None,
        age=age,
        weight_kg=weight_kg,
        photo_url=photo_url or None,
        is_deleted=False,
    )

    db.add(dog)
    db.commit()


def update_dog_backoffice(
    db: Session,
    dog_id: str,
    name: str,
    breed_id: str | None,
    age: int | None,
    weight_kg: float | None,
    photo_url: str | None,
) -> None:
    # Update a dog from backoffice.
    dog = get_backoffice_dog(db=db, dog_id=dog_id)

    if dog:
        dog.name = name
        dog.breed_id = breed_id or None
        dog.age = age
        dog.weight_kg = weight_kg
        dog.photo_url = photo_url or None
        db.commit()


def soft_delete_dog_backoffice(db: Session, dog_id: str) -> None:
    # Soft delete a dog and deactivate its active device link.
    dog = get_backoffice_dog(db=db, dog_id=dog_id)

    if not dog:
        return

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


def delete_dog_permanently(db: Session, dog_id: str) -> None:
    # Permanently delete a dog.
    dog = get_backoffice_dog(db=db, dog_id=dog_id)

    if dog:
        db.delete(dog)
        db.commit()


def list_backoffice_links(db: Session) -> list[DogDevice]:
    # Return all dog-device links.
    return db.query(DogDevice).order_by(DogDevice.created_at.desc()).all()


def unlink_device_backoffice(db: Session, link_id: str) -> None:
    # Deactivate a dog-device link.
    link = db.query(DogDevice).filter(DogDevice.id == link_id).first()

    if link:
        link.is_active = False
        db.commit()


def delete_link_permanently(db: Session, link_id: str) -> None:
    # Permanently delete a dog-device link.
    link = db.query(DogDevice).filter(DogDevice.id == link_id).first()

    if link:
        db.delete(link)
        db.commit()


def delete_device_permanently(db: Session, device_id: str) -> None:
    # Permanently delete a physical device.
    device = db.query(Device).filter(Device.device_id == device_id).first()

    if device:
        db.delete(device)
        db.commit()