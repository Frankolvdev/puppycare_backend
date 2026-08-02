from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.app.app_user import AppUser
from app.schemas.user import CompleteProfileRequest, UserMeResponse
from app.services.auth_service import create_optional_dog, get_missing_profile_fields

router = APIRouter()


@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Get current user",
)
def get_me(
    current_user: AppUser = Depends(get_current_user),
):
    # Return the authenticated user.
    missing_fields = get_missing_profile_fields(current_user)

    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "photo_url": current_user.photo_url,
        "phone": current_user.phone,
        "user_type": current_user.user_type,
        "profile_completed": len(missing_fields) == 0,
    }


@router.put(
    "/profile",
    response_model=UserMeResponse,
    summary="Complete user profile",
)
def complete_profile(
    payload: CompleteProfileRequest,
    db: Session = Depends(get_db),
    current_user: AppUser = Depends(get_current_user),
):
    # Complete missing profile data after Google login or partial signup.
    if payload.phone is not None:
        current_user.phone = payload.phone

    if payload.user_type is not None:
        current_user.user_type = payload.user_type

    db.commit()
    db.refresh(current_user)

    create_optional_dog(db=db, user=current_user, dog_payload=payload.dog)

    missing_fields = get_missing_profile_fields(current_user)

    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "photo_url": current_user.photo_url,
        "phone": current_user.phone,
        "user_type": current_user.user_type,
        "profile_completed": len(missing_fields) == 0,
    }