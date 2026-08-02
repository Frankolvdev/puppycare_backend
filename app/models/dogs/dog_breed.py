from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class DogBreed(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    # Dog breed medical reference values.
    __tablename__ = "dog_breeds"
    __table_args__ = {"schema": "dogs"}

    name: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)

    heart_rate_min: Mapped[int] = mapped_column(Integer, nullable=False)
    heart_rate_max: Mapped[int] = mapped_column(Integer, nullable=False)

    temperature_min: Mapped[float] = mapped_column(Float, nullable=False)
    temperature_max: Mapped[float] = mapped_column(Float, nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)