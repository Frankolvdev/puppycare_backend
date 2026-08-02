import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.devices.device import Device


class DeviceReading(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    # Stores every telemetry reading sent by the physical device.
    __tablename__ = "device_readings"
    __table_args__ = {"schema": "devices"}

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    internet_connected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    module: Mapped[str | None] = mapped_column(String(100), nullable=True)
    apn: Mapped[str | None] = mapped_column(String(150), nullable=True)

    dog_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    ambient_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    pulse_raw: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heart_bpm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    battery: Mapped[int | None] = mapped_column(Integer, nullable=True)

    gps_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    gps_lon: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Physical device that sent this telemetry reading.
    device: Mapped["Device"] = relationship(
        back_populates="readings",
        lazy="selectin",
    )