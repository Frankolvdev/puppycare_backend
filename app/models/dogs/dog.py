import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.app.app_user import AppUser
    from app.models.dogs.dog_breed import DogBreed
    from app.models.dogs.dog_device import DogDevice


class Dog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    # Dog profile created by an app user.
    __tablename__ = "dogs"
    __table_args__ = {"schema": "dogs"}

    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("app.app_users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    breed_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dogs.dog_breeds.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    # Legacy/free-text breed field. We keep it for compatibility.
    breed: Mapped[str | None] = mapped_column(String(120), nullable=True)

    age: Mapped[int | None] = mapped_column(nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # App user who owns this dog profile.
    owner: Mapped["AppUser"] = relationship(
        back_populates="dogs",
        lazy="selectin",
    )

    # Selected breed reference with health ranges.
    breed_ref: Mapped["DogBreed | None"] = relationship(
        lazy="selectin",
    )

    # Device links for this dog profile.
    device_links: Mapped[list["DogDevice"]] = relationship(
        back_populates="dog",
        cascade="all, delete-orphan",
        lazy="selectin",
    )