from decimal import Decimal

import pytest

from app.events.enums import ActivityEventTypeEnum
from app.events.models import ActivityEvent
from tests.factories.activity_event_factory import ActivityEventFactory


@pytest.fixture
def withdraw_activity_events_as_model() -> list[ActivityEvent]:
    return [
        ActivityEventFactory(
            is_default_user=True,
            is_withdraw=True,
            is_received=True,
            event_received_at=1577836802,
        ),
        ActivityEventFactory(
            is_default_user=True,
            is_withdraw=True,
            is_received=True,
            event_received_at=1577836801,
        ),
        ActivityEventFactory(
            is_default_user=True,
            is_deposit=True,
            is_received=True,
            event_received_at=1577836799,
        ),
    ]


@pytest.fixture
def deposit_activity_events_as_model() -> list[ActivityEvent]:
    return [
        ActivityEventFactory(
            is_default_user=True,
            transaction_type=ActivityEventTypeEnum.DEPOSIT,
            amount=Decimal("75.00"),
            is_received=True,
            event_received_at=1577836802,
        ),
        ActivityEventFactory(
            is_default_user=True,
            transaction_type=ActivityEventTypeEnum.DEPOSIT,
            amount=Decimal("50.00"),
            is_received=True,
            event_received_at=1577836801,
        ),
        ActivityEventFactory(
            is_default_user=True,
            is_withdraw=True,
            is_received=True,
            event_received_at=1577836799,
        ),
    ]
