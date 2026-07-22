import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.shared import TimestampMixin


class ResourceType(str, enum.Enum):
    desk = "desk"
    room = "room"
    equipment = "equipment"


class Resource(Base, TimestampMixin):
    __tablename__ = "resources"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType), nullable=False
    )
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    credit_cost_per_hour: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=1.0
    )
    space_id: Mapped[str] = mapped_column(
        ForeignKey("spaces.id", ondelete="CASCADE"), nullable=False, index=True
    )

    space: Mapped["Space"] = relationship(back_populates="resources") # type: ignore
