import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.dog import Dog
    from app.models.user_auth_account import UserAuthAccount


class AppUser(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    # End users who use the Flutter mobile app.
    __tablename__ = "app_users"
    __table_args__ = {"schema": "app"}

    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    user_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    

    # Authentication methods linked to this user, such as email, Google, or Facebook.
    auth_accounts: Mapped[list["UserAuthAccount"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # Dog profiles owned by this app user.
    dogs: Mapped[list["Dog"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )