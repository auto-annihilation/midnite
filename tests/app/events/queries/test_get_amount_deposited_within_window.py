from decimal import Decimal

import pytest
from freezegun import freeze_time

from app import db
from app.events.controllers import (
    get_amount_deposited_within_window,
)
from app.events.models import ActivityEvent
from tests.factories.activity_event_factory import ActivityEventFactory


@pytest.fixture
def deposit_activity_events_as_model() -> list[ActivityEvent]:
    return [
        ActivityEventFactory(
            is_default_user=True,
            is_deposit=True,
            event_received_at=1577836799,
        ),
        ActivityEventFactory(
            is_default_user=True,
            is_deposit=True,
            event_received_at=1577836800,
        ),
        ActivityEventFactory(
            is_default_user=True,
            is_withdraw=True,
            event_received_at=1577836801,
        ),
        ActivityEventFactory(
            is_default_user=True,
            is_deposit=True,
            event_received_at=1577836802,
        ),
    ]


@freeze_time("2020-01-01T00:00:00+00:00")
def test_get_amount_deposited_within_window(
    deposit_activity_events_as_model: list[ActivityEvent],
) -> None:
    db.save_all(models=deposit_activity_events_as_model)

    deposited_amount: int = get_amount_deposited_within_window(user_id=1)

    assert deposited_amount == Decimal("300.00")


@freeze_time("2020-01-01T00:00:00+00:00")
def test_get_amount_deposited_for_user_outside_window(
    deposit_activity_events_as_model: list[ActivityEvent],
) -> None:
    db.save_all(models=deposit_activity_events_as_model)

    with freeze_time("2020-01-01T00:00:31+00:00"):
        deposited_amount: int = get_amount_deposited_within_window(user_id=1)

    assert deposited_amount == Decimal("100.00")


def test_get_amount_deposited_within_window_without_data() -> None:
    deposited_amount: int = get_amount_deposited_within_window(user_id=1)

    assert deposited_amount == Decimal("0.00")
