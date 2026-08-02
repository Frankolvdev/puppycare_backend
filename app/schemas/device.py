from pydantic import BaseModel, Field


class DeviceReadingRequest(BaseModel):
    # Payload sent by the physical device.
    device_id: str
    internet_connected: bool
    module: str | None = None
    apn: str | None = None
    dog_temperature: float | None = None
    ambient_temperature: float | None = None
    pulse_raw: int | None = None
    heart_bpm: int | None = None
    battery: int | None = None
    gps_lat: str | float | None = None
    gps_lon: str | float | None = None


class DeviceReadingResponse(BaseModel):
    # Response returned after storing the reading.
    status: str
    device_id: str
    reading_saved: bool


class AdminCreateDeviceRequest(BaseModel):
    # Device creation payload used by the backoffice.
    device_id: str = Field(min_length=3, max_length=100)
    module: str | None = None
    apn: str | None = None


class AdminUpdateDeviceRequest(BaseModel):
    # Device update payload used by the backoffice.
    module: str | None = None
    apn: str | None = None
    is_active: bool = True


class DeviceResponse(BaseModel):
    # Device response used by the API.
    id: str
    device_id: str
    module: str | None
    apn: str | None
    is_active: bool


class LinkDeviceRequest(BaseModel):
    # Payload used to link a device to a dog profile.
    dog_id: str
    device_id: str


class LinkDeviceResponse(BaseModel):
    # Response returned after linking a device.
    status: str
    dog_id: str
    device_id: str
    linked: bool