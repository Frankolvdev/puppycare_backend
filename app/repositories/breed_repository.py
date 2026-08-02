from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.dogs.dog_breed import DogBreed


def list_breeds(db: Session) -> list[DogBreed]:
    # Return all dog breeds ordered by name.
    return db.query(DogBreed).order_by(DogBreed.name.asc()).all()


def create_breed(
    db: Session,
    name: str,
    heart_rate_min: int,
    heart_rate_max: int,
    temperature_min: float,
    temperature_max: float,
) -> DogBreed:
    # Create a new dog breed reference.
    existing = db.query(DogBreed).filter(DogBreed.name == name).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Breed already exists.",
        )

    breed = DogBreed(
        name=name,
        heart_rate_min=heart_rate_min,
        heart_rate_max=heart_rate_max,
        temperature_min=temperature_min,
        temperature_max=temperature_max,
        is_active=True,
    )

    db.add(breed)
    db.commit()
    db.refresh(breed)

    return breed


def update_breed(
    db: Session,
    breed_id: str,
    name: str,
    heart_rate_min: int,
    heart_rate_max: int,
    temperature_min: float,
    temperature_max: float,
    is_active: bool,
) -> DogBreed:
    # Update dog breed reference values.
    breed = db.query(DogBreed).filter(DogBreed.id == breed_id).first()

    if not breed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Breed not found.",
        )

    breed.name = name
    breed.heart_rate_min = heart_rate_min
    breed.heart_rate_max = heart_rate_max
    breed.temperature_min = temperature_min
    breed.temperature_max = temperature_max
    breed.is_active = is_active

    db.commit()
    db.refresh(breed)

    return breed


def delete_breed_permanently(db: Session, breed_id: str) -> None:
    # Permanently delete a breed reference from the database.
    breed = db.query(DogBreed).filter(DogBreed.id == breed_id).first()

    if breed:
        db.delete(breed)
        db.commit()