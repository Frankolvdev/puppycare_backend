from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.devices.device_reading import DeviceReading
    from app.models.dogs.dog_device import DogDevice


class Device(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    # Physical GPS/health tracking device installed on the dog collar.
    __tablename__ = "devices"
    __table_args__ = {"schema": "devices"}

    device_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    module: Mapped[str | None] = mapped_column(String(100), nullable=True)
    apn: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Dog links related to this physical device.
    dog_links: Mapped[list["DogDevice"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Telemetry readings sent by this device.
    readings: Mapped[list["DeviceReading"]] = relationship(
        back_populates="device",
        cascade="all, delete-orphan",
        lazy="selectin",
    )