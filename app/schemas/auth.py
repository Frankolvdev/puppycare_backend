from pydantic import BaseModel, EmailStr, Field


class RegisterDogRequest(BaseModel):
    # Optional dog profile created during signup or profile completion.
    name: str = Field(min_length=1, max_length=120)
    breed: str | None = None
    age: int | None = None
    weight_kg: float | None = None
    photo_url: str | None = None


class RegisterRequest(BaseModel):
    # Email/password registration payload.
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    phone: str | None = None
    user_type: str | None = None
    dog: RegisterDogRequest | None = None


class LoginRequest(BaseModel):
    # Email/password login payload.
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class GoogleLoginRequest(BaseModel):
    # Google ID token payload.
    id_token: str


class AuthResponse(BaseModel):
    # Auth response used by email/password and Google.
    access_token: str
    token_type: str = "bearer"
    profile_completed: bool
    missing_fields: list[str]


class TokenResponse(AuthResponse):
    pass