# Import all models here so Alembic can detect them later.

from app.models.app.app_user import AppUser
from app.models.auth.staff_user import StaffUser
from app.models.auth.user_auth_account import UserAuthAccount
from app.models.devices.device import Device
from app.models.devices.device_reading import DeviceReading
from app.models.dogs.dog import Dog
from app.models.dogs.dog_device import DogDevice
from app.models.dogs.dog_breed import DogBreed