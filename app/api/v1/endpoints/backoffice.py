from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.dependencies.backoffice_auth import get_current_staff
from app.models.app.app_user import AppUser
from app.models.auth.staff_user import StaffUser
from app.models.devices.device import Device
from app.models.dogs.dog import Dog
from app.models.dogs.dog_device import DogDevice
from app.repositories.backoffice_repository import (
    create_dog_backoffice,
    delete_dog_permanently,
    delete_link_permanently,
    delete_user_permanently,
    delete_device_permanently,
    get_backoffice_user,
    list_backoffice_dogs,
    list_backoffice_links,
    list_backoffice_users,
    list_user_dogs_backoffice,
    soft_delete_dog_backoffice,
    unlink_device_backoffice,
    update_dog_backoffice,
    update_user_backoffice,
)
from app.repositories.breed_repository import (
    create_breed,
    delete_breed_permanently,
    list_breeds,
    update_breed,
)
from app.repositories.staff_repository import (
    create_staff_user,
    delete_staff_user_permanently,
    get_staff_by_email,
    list_staff_users,
    update_staff_user,
)
from app.schemas.device import AdminCreateDeviceRequest, AdminUpdateDeviceRequest
from app.services.admin_device_service import (
    activate_device_from_backoffice,
    create_device_from_backoffice,
    deactivate_device_from_backoffice,
    get_devices_for_backoffice,
    update_device_from_backoffice,
)

import time
from fastapi import HTTPException, status
from app.models.devices.device_reading import DeviceReading


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    # Render the backoffice login page.
    return templates.TemplateResponse(request=request, name="backoffice/login.html", context={"error": None})


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    # Authenticate staff user and create session.
    staff = get_staff_by_email(db=db, email=email)

    if not staff or not staff.is_active or not verify_password(password, staff.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="backoffice/login.html",
            context={"error": "Invalid email or password."},
            status_code=401,
        )

    request.session["staff_id"] = str(staff.id)
    return RedirectResponse(url="/backoffice/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    # Clear the backoffice session.
    request.session.clear()
    return RedirectResponse(url="/backoffice/login", status_code=303)


@router.get("/")
def backoffice_root():
    # Redirect root to dashboard.
    return RedirectResponse(url="/backoffice/dashboard", status_code=303)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Render dashboard with basic stats.
    stats = {
        "users": db.query(AppUser).count(),
        "dogs": db.query(Dog).filter(Dog.is_deleted == False).count(),
        "devices": db.query(Device).count(),
        "links": db.query(DogDevice).filter(DogDevice.is_active == True).count(),
    }

    recent_devices = db.query(Device).order_by(Device.created_at.desc()).limit(5).all()

    return templates.TemplateResponse(
        request=request,
        name="backoffice/dashboard.html",
        context={"current_staff": current_staff, "stats": stats, "recent_devices": recent_devices},
    )


@router.get("/devices", response_class=HTMLResponse)
def devices_page(
    request: Request,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Render devices management page.
    devices = get_devices_for_backoffice(db=db)

    return templates.TemplateResponse(
        request=request,
        name="backoffice/devices.html",
        context={"devices": devices, "current_staff": current_staff},
    )


@router.post("/devices")
def create_device_from_form(
    device_id: str = Form(...),
    module: str | None = Form(None),
    apn: str | None = Form(None),
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    device_id_clean = device_id.strip()

    existing_device = (
        db.query(Device)
        .filter(Device.device_id == device_id_clean)
        .first()
    )

    if existing_device:
        return JSONResponse(
            status_code=409,
            content={"detail": "Este Device ID ya está registrado."},
        )

    payload = AdminCreateDeviceRequest(
        device_id=device_id_clean,
        module=module or None,
        apn=apn or None,
    )

    create_device_from_backoffice(db=db, payload=payload)

    device = (
        db.query(Device)
        .filter(Device.device_id == device_id_clean)
        .first()
    )

    if not device:
        return JSONResponse(
            status_code=500,
            content={"detail": "No se pudo crear el dispositivo."},
        )

    last_reading = (
        db.query(DeviceReading)
        .filter(DeviceReading.device_id == device.id)
        .order_by(DeviceReading.created_at.desc())
        .first()
    )

    baseline_created_at = last_reading.created_at if last_reading else None

    timeout_seconds = 60
    interval_seconds = 3
    started_at = time.time()

    while time.time() - started_at < timeout_seconds:
        db.expire_all()

        still_exists = (
            db.query(Device)
            .filter(Device.id == device.id)
            .first()
        )

        if not still_exists:
            return JSONResponse(
                status_code=499,
                content={"detail": "Registro cancelado."},
            )

        latest_reading = (
            db.query(DeviceReading)
            .filter(DeviceReading.device_id == device.id)
            .order_by(DeviceReading.created_at.desc())
            .first()
        )

        has_new_reading = (
            baseline_created_at is None and latest_reading is not None
        ) or (
            baseline_created_at is not None
            and latest_reading is not None
            and latest_reading.created_at > baseline_created_at
        )

        if has_new_reading:
            return JSONResponse(
                status_code=200,
                content={"detail": "Dispositivo registrado correctamente."},
            )

        time.sleep(interval_seconds)

    delete_device_permanently(db=db, device_id=str(device.id))

    return JSONResponse(
        status_code=408,
        content={
            "detail": "No se detectó señal. Mantenga el dispositivo encendido y con conexión a la red."
        },
    )


@router.post("/devices/{device_id}/update")
def update_device_from_form(
    device_id: str,
    module: str | None = Form(None),
    apn: str | None = Form(None),
    is_active: str | None = Form(None),
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Update device from form.
    payload = AdminUpdateDeviceRequest(module=module or None, apn=apn or None, is_active=is_active == "true")
    update_device_from_backoffice(db=db, device_id=device_id, payload=payload)
    return RedirectResponse(url="/backoffice/devices", status_code=303)


@router.post("/devices/{device_id}/deactivate")
def deactivate_device_from_form(
    device_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Deactivate device from form.
    deactivate_device_from_backoffice(db=db, device_id=device_id)
    return RedirectResponse(url="/backoffice/devices", status_code=303)


@router.post("/devices/{device_id}/activate")
def activate_device_from_form(
    device_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Activate device from form.
    activate_device_from_backoffice(db=db, device_id=device_id)
    return RedirectResponse(url="/backoffice/devices", status_code=303)


@router.post("/devices/{device_id}/delete")
def delete_device_from_form(
    device_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Permanently delete device from database.
    delete_device_permanently(db=db, device_id=device_id)
    return RedirectResponse(url="/backoffice/devices", status_code=303)


@router.get("/users", response_class=HTMLResponse)
def users_page(
    request: Request,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Render users management page.
    users = list_backoffice_users(db=db)

    return templates.TemplateResponse(
        request=request,
        name="backoffice/users.html",
        context={"current_staff": current_staff, "users": users},
    )


@router.get("/users/{user_id}", response_class=HTMLResponse)
def user_detail_page(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Render one user's dog list.
    user = get_backoffice_user(db=db, user_id=user_id)
    dogs = list_user_dogs_backoffice(db=db, user_id=user_id)
    breeds = list_breeds(db=db)

    return templates.TemplateResponse(
        request=request,
        name="backoffice/user_detail.html",
        context={"current_staff": current_staff, "user": user, "dogs": dogs, "breeds": breeds},
    )


@router.post("/users/{user_id}/update")
def update_user_from_form(
    user_id: str,
    name: str | None = Form(None),
    email: str | None = Form(None),
    is_active: str | None = Form(None),
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Update app user from form.
    update_user_backoffice(db=db, user_id=user_id, name=name or None, email=email or None, is_active=is_active == "true")
    return RedirectResponse(url="/backoffice/users", status_code=303)


@router.post("/users/{user_id}/delete")
def delete_user_from_form(
    user_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Permanently delete app user.
    delete_user_permanently(db=db, user_id=user_id)
    return RedirectResponse(url="/backoffice/users", status_code=303)


@router.post("/users/{user_id}/dogs")
def create_dog_for_user_from_form(
    user_id: str,
    name: str = Form(...),
    breed_id: str | None = Form(None),
    age: int | None = Form(None),
    weight_kg: float | None = Form(None),
    photo_url: str | None = Form(None),
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Create dog for selected user.
    create_dog_backoffice(
        db=db,
        owner_id=user_id,
        name=name,
        breed_id=breed_id or None,
        age=age,
        weight_kg=weight_kg,
        photo_url=photo_url or None,
    )
    return RedirectResponse(url=f"/backoffice/users/{user_id}", status_code=303)


@router.get("/dogs", response_class=HTMLResponse)
def dogs_page(
    request: Request,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Render dogs management page.
    dogs = list_backoffice_dogs(db=db)
    breeds = list_breeds(db=db)

    return templates.TemplateResponse(
        request=request,
        name="backoffice/dogs.html",
        context={"current_staff": current_staff, "dogs": dogs, "breeds": breeds},
    )


@router.post("/dogs/{dog_id}/update")
def update_dog_from_form(
    dog_id: str,
    name: str = Form(...),
    breed_id: str | None = Form(None),
    age: int | None = Form(None),
    weight_kg: float | None = Form(None),
    photo_url: str | None = Form(None),
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Update dog from form.
    update_dog_backoffice(
        db=db,
        dog_id=dog_id,
        name=name,
        breed_id=breed_id or None,
        age=age,
        weight_kg=weight_kg,
        photo_url=photo_url or None,
    )
    return RedirectResponse(url="/backoffice/dogs", status_code=303)


@router.post("/dogs/{dog_id}/delete")
def delete_dog_from_form(
    dog_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Soft delete dog from backoffice.
    soft_delete_dog_backoffice(db=db, dog_id=dog_id)
    return RedirectResponse(url="/backoffice/dogs", status_code=303)


@router.post("/dogs/{dog_id}/delete-permanent")
def delete_dog_permanently_from_form(
    dog_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Permanently delete dog from database.
    delete_dog_permanently(db=db, dog_id=dog_id)
    return RedirectResponse(url="/backoffice/dogs", status_code=303)


@router.get("/links", response_class=HTMLResponse)
def links_page(
    request: Request,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Render dog-device links page.
    links = list_backoffice_links(db=db)

    return templates.TemplateResponse(
        request=request,
        name="backoffice/links.html",
        context={"current_staff": current_staff, "links": links},
    )


@router.post("/links/{link_id}/unlink")
def unlink_device_from_form(
    link_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Unlink device from dog.
    unlink_device_backoffice(db=db, link_id=link_id)
    return RedirectResponse(url="/backoffice/links", status_code=303)


@router.post("/links/{link_id}/delete")
def delete_link_from_form(
    link_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Permanently delete dog-device link.
    delete_link_permanently(db=db, link_id=link_id)
    return RedirectResponse(url="/backoffice/links", status_code=303)


@router.get("/breeds", response_class=HTMLResponse)
def breeds_page(
    request: Request,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Render dog breeds management page.
    breeds = list_breeds(db=db)

    return templates.TemplateResponse(
        request=request,
        name="backoffice/breeds.html",
        context={"current_staff": current_staff, "breeds": breeds},
    )


@router.post("/breeds")
def create_breed_from_form(
    name: str = Form(...),
    heart_rate_min: int = Form(...),
    heart_rate_max: int = Form(...),
    temperature_min: float = Form(...),
    temperature_max: float = Form(...),
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Create dog breed from backoffice form.
    create_breed(db, name, heart_rate_min, heart_rate_max, temperature_min, temperature_max)
    return RedirectResponse(url="/backoffice/breeds", status_code=303)


@router.post("/breeds/{breed_id}/update")
def update_breed_from_form(
    breed_id: str,
    name: str = Form(...),
    heart_rate_min: int = Form(...),
    heart_rate_max: int = Form(...),
    temperature_min: float = Form(...),
    temperature_max: float = Form(...),
    is_active: str | None = Form(None),
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Update dog breed from backoffice form.
    update_breed(db, breed_id, name, heart_rate_min, heart_rate_max, temperature_min, temperature_max, is_active == "true")
    return RedirectResponse(url="/backoffice/breeds", status_code=303)


@router.post("/breeds/{breed_id}/delete")
def delete_breed_from_form(
    breed_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Permanently delete breed from database.
    delete_breed_permanently(db=db, breed_id=breed_id)
    return RedirectResponse(url="/backoffice/breeds", status_code=303)


@router.get("/admins", response_class=HTMLResponse)
def admins_page(
    request: Request,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Render staff administrators page.
    admins = list_staff_users(db=db)

    return templates.TemplateResponse(
        request=request,
        name="backoffice/admins.html",
        context={"current_staff": current_staff, "admins": admins},
    )


@router.post("/admins")
def create_admin_from_form(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("admin"),
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Create staff administrator.
    create_staff_user(db=db, name=name, email=email, password_hash=hash_password(password), role=role)
    return RedirectResponse(url="/backoffice/admins", status_code=303)


@router.post("/admins/{staff_id}/update")
def update_admin_from_form(
    staff_id: str,
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    is_active: str | None = Form(None),
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Update staff administrator.
    update_staff_user(db=db, staff_id=staff_id, name=name, email=email, role=role, is_active=is_active == "true")
    return RedirectResponse(url="/backoffice/admins", status_code=303)


@router.post("/admins/{staff_id}/delete")
def delete_admin_from_form(
    staff_id: str,
    db: Session = Depends(get_db),
    current_staff: StaffUser = Depends(get_current_staff),
):
    # Permanently delete staff administrator.
    delete_staff_user_permanently(db=db, staff_id=staff_id)
    return RedirectResponse(url="/backoffice/admins", status_code=303)