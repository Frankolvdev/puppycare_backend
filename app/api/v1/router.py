from fastapi import APIRouter
from app.api.v1.endpoints import (
    admin,
    auth,
    devices,
    dogs,
    users,
    backoffice,
    uploads
)

router = APIRouter()

router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication"],
)

router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"],
)

router.include_router(
    dogs.router,
    prefix="/dogs",
    tags=["Dogs"],
)

router.include_router(
    devices.router,
    prefix="/devices",
    tags=["Devices"],
)

router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Administration"],
)

router.include_router(
    backoffice.router,
    prefix="/backoffice",
    tags=["Backoffice"],
)

router.include_router(
    uploads.router,
    prefix="/uploads",
    tags=["Uploads"],
)