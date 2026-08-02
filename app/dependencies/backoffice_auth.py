from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.auth.staff_user import StaffUser
from app.repositories.staff_repository import get_staff_by_id


def get_current_staff(
    request: Request,
    db: Session = Depends(get_db),
) -> StaffUser:
    """
    Get the current logged-in staff user from the session cookie.
    """
    staff_id = request.session.get("staff_id")

    if not staff_id:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/backoffice/login"},
        )

    staff = get_staff_by_id(db=db, staff_id=staff_id)

    if not staff or not staff.is_active:
        request.session.clear()

        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": "/backoffice/login"},
        )

    return staff