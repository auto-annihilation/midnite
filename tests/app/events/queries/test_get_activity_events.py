from uuid import UUID, uuid4

import pytest
from freezegun import freeze_time

from app import db
from app.events.enums import ActivityEventTypeEnum
from app.events.models import ActivityEvent
from app.events.queries import get_activity_events
from tests.factories.activity_event_factory import ActivityEventFactory


@pytest.fixture
def first_event_uuid() -> UUID:
    return uuid4()


@pytest.fixture
def second_event_uuid() -> UUID:
    return uuid4()


@pytest.fixture
def third_event_uuid() -> UUID:
    return uuid4()


@pytest.fixture
def fourth_event_uuid() -> UUID:
    return uuid4()


@pytest.fixture
def fifth_event_uuid() -> UUID:
    return uuid4()


@pytest.fixture
def sixth_event_uuid() -> UUID:
    return uuid4()


@pytest.fixture
def ordered_activity_events_as_model(
    first_event_uuid: UUID,
    second_event_uuid: UUID,
    third_event_uuid: UUID,
    fourth_event_uuid: UUID,
    fifth_event_uuid: UUID,
    sixth_event_uuid: UUID,
) -> list[ActivityEvent]:
    return [
        ActivityEventFactory(
            id=first_event_uuid,
            is_default_user=True,
            is_deposit=True,
            is_received=True,
            event_received_at=1577836799,
        ),
        ActivityEventFactory(
            id=second_event_uuid,
            is_default_user=True,
            is_deposit=True,
            is_received=True,
            event_received_at=1577836800,
        ),
        ActivityEventFactory(
            id=third_event_uuid,
            is_default_user=True,
            is_withdraw=True,
            is_received=True,
            event_received_at=1577836801,
        ),
        ActivityEventFactory(
            id=fourth_event_uuid,
            is_default_user=True,
            is_deposit=True,
            is_received=True,
            event_received_at=1577836802,
        ),
        ActivityEventFactory(
            id=fifth_event_uuid,
            user_id=2,
            is_withdraw=True,
            is_received=True,
            event_received_at=1577836803,
        ),
        ActivityEventFactory(
            id=sixth_event_uuid,
            user_id=2,
            is_deposit=True,
            is_received=True,
            event_received_at=1577836804,
        ),
    ]


@freeze_time("2020-01-01T00:00:00+00:00")
def test_get_activity_events(
    ordered_activity_events_as_model: list[ActivityEvent],
    first_event_uuid: UUID,
    second_event_uuid: UUID,
    third_event_uuid: UUID,
    fourth_event_uuid: UUID,
    fifth_event_uuid: UUID,
    sixth_event_uuid: UUID,
) -> None:
    db.save_all(models=ordered_activity_events_as_model)

    activity_events: list[ActivityEvent] = get_activity_events()

    assert len(activity_events) == 6
    assert activity_events[0].id == sixth_event_uuid
    assert activity_events[1].id == fifth_event_uuid
    assert activity_events[2].id == fourth_event_uuid
    assert activity_events[3].id == third_event_uuid
    assert activity_events[4].id == second_event_uuid
    assert activity_events[5].id == first_event_uuid


@freeze_time("2020-01-01T00:00:00+00:00")
def test_get_activity_events_for_user(
    ordered_activity_events_as_model: list[ActivityEvent],
    first_event_uuid: UUID,
    second_event_uuid: UUID,
    third_event_uuid: UUID,
    fourth_event_uuid: UUID,
) -> None:
    db.save_all(models=ordered_activity_events_as_model)

    activity_events: list[ActivityEvent] = get_activity_events(user_id=1)

    assert len(activity_events) == 4
    assert activity_events[0].id == fourth_event_uuid
    assert activity_events[1].id == third_event_uuid
    assert activity_events[2].id == second_event_uuid
    assert activity_events[3].id == first_event_uuid


@freeze_time("2020-01-01T00:00:00+00:00")
def test_get_activity_events_for_user_filtered_by_deposit_transaction_type(
    ordered_activity_events_as_model: list[ActivityEvent],
    first_event_uuid: UUID,
    second_event_uuid: UUID,
    fourth_event_uuid: UUID,
) -> None:
    db.save_all(models=ordered_activity_events_as_model)

    activity_events: list[ActivityEvent] = get_activity_events(
        user_id=1,
        transaction_type=ActivityEventTypeEnum.DEPOSIT,
    )

    assert len(activity_events) == 3
    assert activity_events[0].id == fourth_event_uuid
    assert activity_events[1].id == second_event_uuid
    assert activity_events[2].id == first_event_uuid


@freeze_time("2020-01-01T00:00:00+00:00")
def test_get_activity_events_for_user_filtered_by_withdraw_transaction_type(
    ordered_activity_events_as_model: list[ActivityEvent],
    third_event_uuid: UUID,
) -> None:
    db.save_all(models=ordered_activity_events_as_model)

    activity_events: list[ActivityEvent] = get_activity_events(
        user_id=1,
        transaction_type=ActivityEventTypeEnum.WITHDRAW,
    )

    assert len(activity_events) == 1
    assert activity_events[0].id == third_event_uuid


def test_get_activity_events_for_user_when_results_do_not_exist() -> None:
    activity_events: list[ActivityEvent] = get_activity_events(user_id=1)

    assert len(activity_events) == 0
