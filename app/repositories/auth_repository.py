from sqlalchemy.orm import Session

from app.models.app.app_user import AppUser
from app.models.auth.user_auth_account import UserAuthAccount


def get_user_by_email(db: Session, email: str) -> AppUser | None:
    # Find an app user by email.
    return db.query(AppUser).filter(AppUser.email == email).first()


def get_email_auth_account(db: Session, email: str) -> UserAuthAccount | None:
    # Find an active email/password authentication account.
    return (
        db.query(UserAuthAccount)
        .filter(
            UserAuthAccount.provider == "email",
            UserAuthAccount.email == email,
            UserAuthAccount.is_active == True,
        )
        .first()
    )


def get_auth_account_by_provider(
    db: Session,
    provider: str,
    provider_user_id: str,
) -> UserAuthAccount | None:
    # Find an auth account by provider and provider user id.
    return (
        db.query(UserAuthAccount)
        .filter(
            UserAuthAccount.provider == provider,
            UserAuthAccount.provider_user_id == provider_user_id,
            UserAuthAccount.is_active == True,
        )
        .first()
    )


def create_auth_account(
    db: Session,
    user_id,
    provider: str,
    provider_user_id: str,
    email: str | None = None,
    password_hash: str | None = None,
    is_verified: bool = False,
) -> UserAuthAccount:
    # Create an authentication account for a user.
    auth_account = UserAuthAccount(
        user_id=user_id,
        provider=provider,
        provider_user_id=provider_user_id,
        email=email,
        password_hash=password_hash,
        is_verified=is_verified,
        is_active=True,
    )

    db.add(auth_account)
    db.flush()

    return auth_account


def create_email_user(
    db: Session,
    name: str,
    email: str,
    password_hash: str,
    phone: str | None = None,
    user_type: str | None = None,
) -> AppUser:
    # Create an app user with email/password auth.
    user = AppUser(
        name=name,
        email=email,
        phone=phone,
        user_type=user_type,
        is_active=True,
    )

    db.add(user)
    db.flush()

    create_auth_account(
        db=db,
        user_id=user.id,
        provider="email",
        provider_user_id=email,
        email=email,
        password_hash=password_hash,
        is_verified=False,
    )

    db.commit()
    db.refresh(user)

    return user


def create_google_user(
    db: Session,
    name: str | None,
    email: str,
    photo_url: str | None,
    google_user_id: str,
) -> AppUser:
    # Create an app user with Google auth.
    user = AppUser(
        name=name,
        email=email,
        photo_url=photo_url,
        is_active=True,
    )

    db.add(user)
    db.flush()

    create_auth_account(
        db=db,
        user_id=user.id,
        provider="google",
        provider_user_id=google_user_id,
        email=email,
        password_hash=None,
        is_verified=True,
    )

    db.commit()
    db.refresh(user)

    return user


def link_google_to_existing_user(
    db: Session,
    user: AppUser,
    google_user_id: str,
    email: str,
) -> None:
    # Link Google authentication to an existing app user.
    create_auth_account(
        db=db,
        user_id=user.id,
        provider="google",
        provider_user_id=google_user_id,
        email=email,
        password_hash=None,
        is_verified=True,
    )

    db.commit()