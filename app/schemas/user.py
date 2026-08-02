from pydantic import BaseModel, EmailStr

from app.schemas.auth import RegisterDogRequest


class UserMeResponse(BaseModel):
    # Authenticated app user response.
    id: str
    name: str | None
    email: EmailStr | None
    photo_url: str | None
    phone: str | None
    user_type: str | None
    profile_completed: bool


class CompleteProfileRequest(BaseModel):
    # Payload used to complete missing user profile data.
    phone: str | None = None
    user_type: str | None = None
    dog: RegisterDogRequest | None = None