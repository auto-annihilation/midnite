from decimal import Decimal

import pytest

from app import db
from app.events.controllers import check_alerts
from app.events.domains import AlertResponseDomain
from app.events.enums import ActivityEventTypeEnum
from app.events.models import ActivityEvent
from lib.utils import get_epoch_now
from tests.factories.activity_event_factory import ActivityEventFactory


@pytest.mark.parametrize(
    ("amount", "transaction_type", "expected"),
    [
        pytest.param(
            Decimal("99.99"),
            ActivityEventTypeEnum.WITHDRAW,
            AlertResponseDomain(
                user_id=1,
                alert=False,
                alert_codes=[],
            ),
            id="withdraw_below_limit",
        ),
        pytest.param(
            Decimal("100.00"),
            ActivityEventTypeEnum.WITHDRAW,
            AlertResponseDomain(
                user_id=1,
                alert=False,
                alert_codes=[],
            ),
            id="withdraw_at_limit",
        ),
        pytest.param(
            Decimal("100.01"),
            ActivityEventTypeEnum.WITHDRAW,
            AlertResponseDomain(
                user_id=1,
                alert=True,
                alert_codes=[1100],
            ),
            id="withdraw_above_limit",
        ),
    ],
)
def test_check_alerts_for_withdraw_limits(
    amount: Decimal,
    transaction_type: ActivityEventTypeEnum,
    expected: AlertResponseDomain,
) -> None:
    activity_event: ActivityEvent = ActivityEvent(
        transaction_type=transaction_type,
        amount=amount,
        user_id=1,
        event_received_at=get_epoch_now(),
    )

    alert_response: AlertResponseDomain = check_alerts(
        user_id=1,
        current_activity_event=activity_event,
    )

    assert alert_response == expected


@pytest.mark.parametrize(
    ("activity_event", "activity_event_history", "expected"),
    [
        pytest.param(
            ActivityEventFactory(
                is_default_user=True,
                is_received=True,
                is_withdraw=True,
            ),
            [],
            AlertResponseDomain(
                user_id=1,
                alert=False,
                alert_codes=[],
            ),
            id="single_withdraw_below_concecutive_limit",
        ),
        pytest.param(
            ActivityEventFactory(
                is_default_user=True,
                is_withdraw=True,
            ),
            [
                ActivityEventFactory(
                    is_default_user=True,
                    is_withdraw=True,
                    is_received=True,
                    event_received_at=1577836799,
                ),
                ActivityEventFactory(
                    is_default_user=True,
                    is_withdraw=True,
                    is_received=True,
                    event_received_at=1577836800,
                ),
            ],
            AlertResponseDomain(
                user_id=1,
                alert=True,
                alert_codes=[30],
            ),
            id="withdraw_limit_exceeds_concecutive_limit",
        ),
    ],
)
def test_check_alerts_for_concecutive_withdraw_limit(
    activity_event: ActivityEvent,
    activity_event_history: list[ActivityEvent],
    expected: AlertResponseDomain,
) -> None:
    db.save_all(models=activity_event_history)

    alert_response: AlertResponseDomain = check_alerts(
        user_id=1,
        current_activity_event=activity_event,
    )

    assert alert_response == expected


@pytest.mark.parametrize(
    ("activity_event", "activity_event_history", "expected"),
    [
        pytest.param(
            ActivityEventFactory(
                is_default_user=True,
                is_received=True,
                is_deposit=True,
            ),
            [],
            AlertResponseDomain(
                user_id=1,
                alert=False,
                alert_codes=[],
            ),
            id="single_deposit_below_concecutive_limit",
        ),
        pytest.param(
            ActivityEventFactory(
                is_default_user=True,
                is_deposit=True,
            ),
            [
                ActivityEventFactory(
                    is_default_user=True,
                    is_deposit=True,
                    is_received=True,
                    event_received_at=1577836799,
                ),
                ActivityEventFactory(
                    is_default_user=True,
                    is_deposit=True,
                    is_received=True,
                    event_received_at=1577836800,
                ),
            ],
            AlertResponseDomain(
                user_id=1,
                alert=False,
                alert_codes=[],
            ),
            id="multiple_deposit_limit_does_not_exceed_concecutive_limit",
        ),
        pytest.param(
            ActivityEventFactory(
                is_default_user=True,
                transaction_type=ActivityEventTypeEnum.DEPOSIT,
                amount=Decimal("100.00"),
            ),
            [
                ActivityEventFactory(
                    is_default_user=True,
                    transaction_type=ActivityEventTypeEnum.DEPOSIT,
                    amount=Decimal("50.00"),
                    is_received=True,
                    event_received_at=1577836799,
                ),
                ActivityEventFactory(
                    is_default_user=True,
                    transaction_type=ActivityEventTypeEnum.DEPOSIT,
                    amount=Decimal("75.00"),
                    is_received=True,
                    event_received_at=1577836800,
                ),
            ],
            AlertResponseDomain(
                user_id=1,
                alert=True,
                alert_codes=[300],
            ),
            id="multiple_deposit_limit_does_exceed_concecutive_limit",
        ),
    ],
)
def test_check_alerts_for_concecutive_deposit_limit(
    activity_event: ActivityEvent,
    activity_event_history: list[ActivityEvent],
    expected: AlertResponseDomain,
) -> None:
    db.save_all(models=activity_event_history)

    alert_response: AlertResponseDomain = check_alerts(
        user_id=1,
        current_activity_event=activity_event,
    )

    assert alert_response == expected


@pytest.mark.parametrize(
    ("activity_event", "activity_event_history", "expected"),
    [
        pytest.param(
            ActivityEventFactory(
                is_default_user=True,
                is_received=True,
                is_deposit=True,
            ),
            [],
            AlertResponseDomain(
                user_id=1,
                alert=False,
                alert_codes=[],
            ),
            id="single_withdraw_below_concecutive_limit",
        ),
    ],
)
def test_check_alerts_for_accumulative_deposits_over_time(
    activity_event: ActivityEvent,
    activity_event_history: list[ActivityEvent],
    expected: AlertResponseDomain,
) -> None:
    db.save_all(models=activity_event_history)

    alert_response: AlertResponseDomain = check_alerts(
        user_id=1,
        current_activity_event=activity_event,
    )

    assert alert_response == expected
