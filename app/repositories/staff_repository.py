from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.auth.staff_user import StaffUser


def get_staff_by_email(db: Session, email: str) -> StaffUser | None:
    # Find a staff user by email.
    return db.query(StaffUser).filter(StaffUser.email == email).first()


def get_staff_by_id(db: Session, staff_id: str) -> StaffUser | None:
    # Find a staff user by ID.
    return db.query(StaffUser).filter(StaffUser.id == staff_id).first()


def list_staff_users(db: Session) -> list[StaffUser]:
    # List all staff users.
    return db.query(StaffUser).order_by(StaffUser.created_at.desc()).all()


def create_staff_user(
    db: Session,
    name: str,
    email: str,
    password_hash: str,
    role: str = "admin",
) -> StaffUser:
    # Create a staff user for the backoffice.
    existing = get_staff_by_email(db=db, email=email)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Staff email already exists.",
        )

    staff = StaffUser(
        name=name,
        email=email,
        password_hash=password_hash,
        role=role,
        is_active=True,
    )

    db.add(staff)
    db.commit()
    db.refresh(staff)

    return staff


def update_staff_user(
    db: Session,
    staff_id: str,
    name: str,
    email: str,
    role: str,
    is_active: bool,
) -> None:
    # Update a staff user.
    staff = get_staff_by_id(db=db, staff_id=staff_id)

    if staff:
        staff.name = name
        staff.email = email
        staff.role = role
        staff.is_active = is_active
        db.commit()


def delete_staff_user_permanently(
    db: Session,
    staff_id: str,
) -> None:
    # Permanently delete a staff user.
    staff = get_staff_by_id(db=db, staff_id=staff_id)

    if staff:
        db.delete(staff)
        db.commit()