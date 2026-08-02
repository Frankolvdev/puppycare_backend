from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    AuthResponse,
    GoogleLoginRequest,
    LoginRequest,
    RegisterRequest,
)
from app.services.auth_service import (
    login_user,
    login_with_google,
    register_user,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    summary="Register a new user",
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    # Register a new app user.
    return register_user(db=db, payload=payload)


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login user",
)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    # Login an existing app user.
    return login_user(db=db, payload=payload)


@router.post(
    "/google",
    response_model=AuthResponse,
    summary="Login or register with Google",
)
def google_login(
    payload: GoogleLoginRequest,
    db: Session = Depends(get_db),
):
    # Login or register user using Google.
    return login_with_google(db=db, payload=payload)