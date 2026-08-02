from pydantic import BaseModel, Field


class CreateDogRequest(BaseModel):
    # Payload used to create a dog profile.
    name: str = Field(min_length=1, max_length=120)
    breed: str | None = None
    age: int | None = None
    weight_kg: float | None = None
    photo_url: str | None = None


class UpdateDogRequest(BaseModel):
    # Payload used to update a dog profile.
    name: str | None = Field(default=None, min_length=1, max_length=120)
    breed: str | None = None
    age: int | None = None
    weight_kg: float | None = None
    photo_url: str | None = None


class DogResponse(BaseModel):
    # Dog profile response.
    id: str
    name: str
    breed: str | None
    age: int | None
    weight_kg: float | None
    photo_url: str | None
    has_device: bool