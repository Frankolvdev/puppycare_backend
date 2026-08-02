from fastapi import HTTPException, status
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.dogs.dog import Dog
from app.repositories.auth_repository import (
    create_email_user,
    create_google_user,
    get_auth_account_by_provider,
    get_email_auth_account,
    get_user_by_email,
    link_google_to_existing_user,
)
from app.schemas.auth import GoogleLoginRequest, LoginRequest, RegisterRequest


def get_missing_profile_fields(user) -> list[str]:
    # Return required missing profile fields.
    missing_fields = []

    if not user.phone:
        missing_fields.append("phone")

    if not user.user_type:
        missing_fields.append("user_type")

    return missing_fields


def build_auth_response(user) -> dict:
    # Build common authentication response.
    missing_fields = get_missing_profile_fields(user)

    return {
        "access_token": create_access_token(subject=str(user.id)),
        "token_type": "bearer",
        "profile_completed": len(missing_fields) == 0,
        "missing_fields": missing_fields,
    }


def create_optional_dog(db: Session, user, dog_payload) -> None:
    # Create dog profile when payload is provided.
    if not dog_payload:
        return

    dog = Dog(
        owner_id=user.id,
        name=dog_payload.name,
        breed=dog_payload.breed,
        age=dog_payload.age,
        weight_kg=dog_payload.weight_kg,
        photo_url=dog_payload.photo_url,
        is_deleted=False,
    )

    db.add(dog)
    db.commit()


def register_user(db: Session, payload: RegisterRequest) -> dict:
    # Register a new app user using email and password.
    existing_user = get_user_by_email(db, payload.email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    password_hash = hash_password(payload.password)

    user = create_email_user(
        db=db,
        name=payload.name,
        email=payload.email,
        password_hash=password_hash,
        phone=payload.phone,
        user_type=payload.user_type,
    )

    create_optional_dog(db=db, user=user, dog_payload=payload.dog)

    return build_auth_response(user)


def login_user(db: Session, payload: LoginRequest) -> dict:
    # Authenticate an app user using email and password.
    auth_account = get_email_auth_account(db, payload.email)

    if not auth_account or not auth_account.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(payload.password, auth_account.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return build_auth_response(auth_account.user)


def login_with_google(db: Session, payload: GoogleLoginRequest) -> dict:
    # Login or register user using a Google ID token.
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google login is not configured.",
        )

    try:
        google_payload = id_token.verify_oauth2_token(
            payload.id_token,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google token.",
        )

    google_user_id = google_payload.get("sub")
    email = google_payload.get("email")
    email_verified = google_payload.get("email_verified", False)
    name = google_payload.get("name")
    photo_url = google_payload.get("picture")

    if not google_user_id or not email or not email_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google account email is not verified.",
        )

    auth_account = get_auth_account_by_provider(
        db=db,
        provider="google",
        provider_user_id=google_user_id,
    )

    if auth_account:
        return build_auth_response(auth_account.user)

    existing_user = get_user_by_email(db=db, email=email)

    if existing_user:
        link_google_to_existing_user(
            db=db,
            user=existing_user,
            google_user_id=google_user_id,
            email=email,
        )

        return build_auth_response(existing_user)

    user = create_google_user(
        db=db,
        name=name,
        email=email,
        photo_url=photo_url,
        google_user_id=google_user_id,
    )

    return build_auth_response(user)