from decimal import Decimal

import pytest
from freezegun import freeze_time

from app.events.controllers import check_withdraw_limit
from app.events.enums import ActivityEventTypeEnum
from app.events.models import ActivityEvent
from lib.utils import get_epoch_now


@freeze_time("2020-01-01T00:00:00+00:00")
@pytest.mark.parametrize(
    ("WITHDRAW_amount", "withdraw_limit", "expected"),
    [
        pytest.param(Decimal("0"), Decimal("100"), False, id="zero_WITHDRAW"),
        pytest.param(
            Decimal("50"),
            Decimal("100"),
            False,
            id="half_of_WITHDRAW_limit",
        ),
        pytest.param(
            Decimal("99.99"),
            Decimal("100"),
            False,
            id="below_WITHDRAW_limit",
        ),
        pytest.param(
            Decimal("100.00"),
            Decimal("100"),
            False,
            id="equal_to_WITHDRAW_limit",
        ),
        pytest.param(
            Decimal("100.01"),
            Decimal("100"),
            True,
            id="exceeds_WITHDRAW_limit",
        ),
        pytest.param(
            Decimal("100.01"),
            Decimal("200"),
            False,
            id="double_the_WITHDRAW_limit",
        ),
        pytest.param(
            Decimal("199.99"),
            Decimal("200"),
            False,
            id="below_increased_WITHDRAW_limit",
        ),
        pytest.param(
            Decimal("200"),
            Decimal("200"),
            False,
            id="matching_increased_WITHDRAW_limit",
        ),
        pytest.param(
            Decimal("201"),
            Decimal("200"),
            True,
            id="exceeds_increased_WITHDRAW_limit",
        ),
    ],
)
def test_check_withdraw_limit(
    WITHDRAW_amount: Decimal,
    withdraw_limit: Decimal,
    expected: bool,
) -> None:
    activity_event: ActivityEvent = ActivityEvent(
        transaction_type=ActivityEventTypeEnum.WITHDRAW,
        amount=WITHDRAW_amount,
        user_id=1,
        event_received_at=get_epoch_now(),
    )

    exceeded_withdraw_limit: bool = check_withdraw_limit(
        activity_event=activity_event,
        withdraw_limit=withdraw_limit,
    )

    assert exceeded_withdraw_limit == expected
