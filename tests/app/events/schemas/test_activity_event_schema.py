from decimal import Decimal

import pytest
from freezegun import freeze_time
from marshmallow import ValidationError

from app.events.domains import ActivityEventDomain
from app.events.enums import ActivityEventTypeEnum
from app.events.schemas import ActivityEventSchema


@pytest.fixture
def activity_event_as_request_payload() -> dict:
    return {
        "type": "deposit",
        "amount": "100.00",
        "user_id": 1,
        "t": 1577836800,
    }


@pytest.fixture
def activity_event_as_payload() -> dict:
    return {
        "type": "deposit",
        "amount": "100.00",
        "user_id": 1,
        "event_received_at": 1577836800,
    }


@pytest.fixture
def activity_event_as_domain() -> ActivityEventDomain:
    return ActivityEventDomain(
        transaction_type=ActivityEventTypeEnum.DEPOSIT,
        amount=Decimal("100.00"),
        user_id=1,
        event_received_at=1577836800,
    )


@freeze_time("2020-01-01T00:00:00+00:00")
def test_valid_schema_load(
    activity_event_as_request_payload: dict,
    activity_event_as_domain: ActivityEventDomain,
) -> None:
    activity_event: ActivityEventDomain = ActivityEventSchema().load(
        activity_event_as_request_payload
    )

    assert activity_event == activity_event_as_domain


def test_valid_schema_load_fails_on_missing_payload() -> None:
    with pytest.raises(ValidationError) as e:
        ActivityEventSchema().load(None)  # type: ignore[call-overload]

    assert e.value.messages == {"_schema": ["Invalid input type."]}


def test_valid_schema_load_fails_on_empty_payload() -> None:
    with pytest.raises(ValidationError) as e:
        ActivityEventSchema().load({})

    assert e.value.messages == {
        "type": ["Missing data for required field."],
        "amount": ["Missing data for required field."],
        "user_id": ["Missing data for required field."],
        "t": ["Missing data for required field."],
    }


def test_valid_schema_dump(
    activity_event_as_request_payload: dict,
    activity_event_as_domain: ActivityEventDomain,
) -> None:
    activity_event: dict = ActivityEventSchema().dump(activity_event_as_domain)

    assert activity_event == activity_event_as_request_payload
