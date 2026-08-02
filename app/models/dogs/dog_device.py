import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.dogs.dog import Dog
    from app.models.devices.device import Device


class DogDevice(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    # Links one dog profile to one physical device.
    __tablename__ = "dog_devices"
    __table_args__ = (
        # This index prevents one active dog from having more than one active device.
        Index(
            "uq_active_device_per_dog",
            "dog_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        # This index prevents one active device from being linked to more than one active dog.
        Index(
            "uq_active_dog_per_device",
            "device_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        {"schema": "dogs"},
    )

    dog_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dogs.dogs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    unlinked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Dog profile linked to this device.
    dog: Mapped["Dog"] = relationship(
        back_populates="device_links",
        lazy="selectin",
    )

    # Physical device linked to this dog profile.
    device: Mapped["Device"] = relationship(
        back_populates="dog_links",
        lazy="selectin",
    )