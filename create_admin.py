from app.core.security import hash_password
from app.db.session import SessionLocal
from app.repositories.staff_repository import create_staff_user, get_staff_by_email

db = SessionLocal()

email = "admin@puppycare.app"
password = "admin12345"

existing = get_staff_by_email(db, email)

if existing:
    print("Admin already exists.")
else:
    create_staff_user(
        db=db,
        name="PuppyCare Admin",
        email=email,
        password_hash=hash_password(password),
        role="admin",
    )
    print("Admin created.")

db.close()