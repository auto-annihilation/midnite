from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy.sql import func

from app.events.constants import (
    ACCUMULATIVE_DEPOSIT_TIME_LIMIT,
)
from app.events.enums import ActivityEventTypeEnum
from app.events.models import ActivityEvent

if TYPE_CHECKING:
    from sqlalchemy import ColumnElement


def get_activity_events(
    user_id: int | None = None,
    transaction_type: ActivityEventTypeEnum | None = None,
    order_by_descending: bool = True,
) -> list[ActivityEvent]:
    """
    Retrieves activity events filtered by user ID and transaction type.

    Args:
        user_id: Optional user ID to filter events by
        transaction_type: Optional transaction type to filter events by

    Returns:
        list[ActivityEvent]: List of activity events sorted by dispatch time in descending order
    """
    filters: list[ColumnElement[bool]] = []

    if user_id:
        filters = [ActivityEvent.user_id == user_id]

    if transaction_type:
        filters.append(ActivityEvent.transaction_type == transaction_type)

    return (
        ActivityEvent.query.filter(*filters)
        .order_by(
            ActivityEvent.event_received_at.desc()
            if order_by_descending
            else ActivityEvent.event_received_at.asc()
        )
        .all()
    )


def get_amount_deposited_within_window(user_id: int) -> int:
    """Calculate total deposits made by a user within a time window.

    Args:
        user_id: ID of user to check deposits for

    Returns:
        int: Total amount deposited within window, 0 if no deposits found
    """
    deposit_activity_window: int = int(
        (
            datetime.now() - timedelta(seconds=ACCUMULATIVE_DEPOSIT_TIME_LIMIT)
        ).timestamp()
    )

    return (
        ActivityEvent.query.filter_by(user_id=user_id)
        .where(
            ActivityEvent.transaction_type == ActivityEventTypeEnum.DEPOSIT,
            ActivityEvent.event_received_at >= deposit_activity_window,
        )
        .with_entities(func.sum(ActivityEvent.amount))
        .scalar()
        or 0
    )
