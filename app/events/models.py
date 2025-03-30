import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import UUID, BigInteger, DateTime, Index, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.testing.entities import ComparableEntity
from sqlalchemy.types import Enum as SQLAlchemyEnum

from app import db
from app.events.enums import ActivityEventTypeEnum
from lib.utils import get_utc_now, get_uuid


class ActivityEvent(db.Model, ComparableEntity):  # type: ignore[name-defined]
    __tablename__ = "activity_event"

    id: Mapped[uuid.UUID] = mapped_column(
        type_=UUID(as_uuid=True), primary_key=True, default=get_uuid, nullable=False
    )

    transaction_type: Mapped[ActivityEventTypeEnum] = mapped_column(
        SQLAlchemyEnum(ActivityEventTypeEnum), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    event_received_at: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True), default=get_utc_now, index=True, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        type_=DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        index=True,
        nullable=False,
    )

    __table_args__ = (
        Index("idx_events_created_by_user", "user_id", "event_received_at"),
    )

    def __repr__(self) -> str:
        return f"<ActivityEvent: {self.id}>"
