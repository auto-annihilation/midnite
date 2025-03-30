from decimal import Decimal

from app.events.constants import (
    ACCUMULATIVE_DEPOSIT_AMOUNT_LIMIT,
    CONSECUTIVE_DEPOSIT_TRANSACTION_LIMIT,
    CONSECUTIVE_WITHDRAW_TRANSACTION_LIMIT,
    SINGLE_WITHDRAW_AMOUNT_LIMIT,
)
from app.events.domains import AlertResponseDomain
from app.events.enums import ActivityEventTypeEnum, AlertCodeEnum
from app.events.models import ActivityEvent
from app.events.queries import (
    get_activity_events,
    get_amount_deposited_within_window,
)


def check_alerts(
    user_id: int,
    current_activity_event: ActivityEvent,
) -> AlertResponseDomain:
    """
    Check user activity for potential alerts based on predefined limits and patterns.

    Alert codes are added when:
    - Single withdraw amount exceeds limit
    - Consecutive withdraws exceed limit
    - Consecutive deposits exceed limit
    - Accumulative deposits over time exceed limit

    Args:
        user_id: The ID of the user to check alerts for
        current_activity_event: The current activity event being processed

    Returns:
        AlertResponseDomain: Alert response containing user_id, alert flag, and list of triggered alert codes
    """
    alert_codes: set[int] = set()

    if check_withdraw_limit(
        activity_event=current_activity_event,
        withdraw_limit=SINGLE_WITHDRAW_AMOUNT_LIMIT,
    ):
        alert_codes.add(int(AlertCodeEnum.WITHDRAWN_LIMIT_EXCEEDED_CODE.value))

    if check_consecutive_withdraws(
        user_id=user_id,
        current_activity_event=current_activity_event,
        concecutive_limit=CONSECUTIVE_WITHDRAW_TRANSACTION_LIMIT,
    ):
        alert_codes.add(int(AlertCodeEnum.CONSECUTIVE_WITHDRAW_CODE.value))

    if check_consecutive_deposits(
        user_id=user_id,
        current_activity_event=current_activity_event,
        concecutive_limit=CONSECUTIVE_DEPOSIT_TRANSACTION_LIMIT,
    ):
        alert_codes.add(AlertCodeEnum.CONSECUTIVE_DEPOSIT_CODE.value)

    if check_accumulative_deposits_over_time(
        user_id=user_id,
        current_activity_event=current_activity_event,
        accumulative_limit=ACCUMULATIVE_DEPOSIT_AMOUNT_LIMIT,
    ):
        alert_codes.add(int(AlertCodeEnum.ACCUMULATIVE_DEPOSIT_CODE.value))

    return AlertResponseDomain(
        user_id=user_id,
        alert=len(alert_codes) > 0,
        alert_codes=list(alert_codes),
    )


def check_withdraw_limit(
    activity_event: ActivityEvent, withdraw_limit: Decimal
) -> bool:
    """
    Check if a withdrawal activity exceeds the specified limit.

    Args:
        activity_event: The activity event to check
        withdraw_limit: Maximum allowed withdrawal amount

    Returns:
        bool: True if event is a withdrawal and exceeds limit, False otherwise
    """
    return (
        activity_event.transaction_type == ActivityEventTypeEnum.WITHDRAW
        and activity_event.amount > withdraw_limit
    )


def check_consecutive_withdraws(
    user_id: int,
    current_activity_event: ActivityEvent,
    concecutive_limit: int,
) -> bool:
    """
    Check if a user has made consecutive withdrawals.

    Args:
        current_activity_event: The current activity event being processed
        concecutive_limit: The number of consecutive withdrawals to check for

    Returns:
        bool: True if user has made the specified number of consecutive withdraws, False otherwise
    """
    historic_concecutive_limit = concecutive_limit - 1

    # Note: the requirements do not specify that for desposits can be ignored so they are included
    # if they should be excluded then adding `transaction_type=ActivityEventTypeEnum.WITHDRAW` to the query
    # would be sufficient for removing them.
    withdraw_activity_events: list[ActivityEvent] = get_activity_events(
        user_id=user_id,
    )

    if not withdraw_activity_events:
        return False

    if current_activity_event.transaction_type != ActivityEventTypeEnum.WITHDRAW:
        return False

    if len(withdraw_activity_events) < historic_concecutive_limit:
        return False

    return all(
        event.transaction_type == ActivityEventTypeEnum.WITHDRAW
        for event in withdraw_activity_events[:historic_concecutive_limit]
    )


def check_consecutive_deposits(
    user_id: int,
    current_activity_event: ActivityEvent,
    concecutive_limit: int,
) -> bool:
    """
    Checks if a user has made a specified number of consecutive deposits
    with an increasing amount.

    Args:
        user_id: The ID of the user to check deposits for
        current_activity_event: The current activity event being processed
        concecutive_limit: The number of consecutive deposits to check for

    Returns:
        bool: True if user has made the specified number of consecutive deposits, False otherwise
    """
    historic_concecutive_limit = concecutive_limit - 1

    # Note: the requirements specify that for deposits, withdraws can be ignored and have been excluded
    filtered_activity_event_history: list[ActivityEvent] = get_activity_events(
        user_id=user_id,
        transaction_type=ActivityEventTypeEnum.DEPOSIT,
        order_by_descending=False,
    )

    if not filtered_activity_event_history:
        return False

    if current_activity_event.transaction_type != ActivityEventTypeEnum.DEPOSIT:
        return False

    if len(filtered_activity_event_history) < historic_concecutive_limit:
        return False

    # check if the deposit amounts are increasing
    deposit_amounts: list[Decimal] = [
        event.amount
        for event in filtered_activity_event_history[:historic_concecutive_limit]
    ] + [current_activity_event.amount]

    for i in range(len(deposit_amounts) - 1):
        if deposit_amounts[i] >= deposit_amounts[i + 1]:
            return False

    return True


def check_accumulative_deposits_over_time(
    user_id: int,
    current_activity_event: ActivityEvent,
    accumulative_limit: Decimal,
) -> bool:
    """
    Check if user's total deposits exceed the accumulative limit within a time window.

    Args:
        user_id: The ID of the user to check deposits for
        current_activity_event: The current activity event being processed
        accumulative_limit: The maximum allowed total deposits

    Returns:
        bool: True if total deposits exceed limit, False otherwise
    """
    deposit_amount: int = get_amount_deposited_within_window(user_id=user_id)

    if current_activity_event.transaction_type != ActivityEventTypeEnum.DEPOSIT:
        return False

    total_deposits: Decimal = deposit_amount + current_activity_event.amount

    return total_deposits > accumulative_limit
