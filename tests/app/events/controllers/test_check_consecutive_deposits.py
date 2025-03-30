from freezegun import freeze_time

from app import db
from app.events.controllers import check_consecutive_deposits
from app.events.models import ActivityEvent
from tests.factories.activity_event_factory import ActivityEventFactory


@freeze_time("2020-01-01T00:00:00+00:00")
def test_check_consecutive_deposits_when_no_history_exists() -> None:
    activity_event: ActivityEvent = ActivityEventFactory(
        is_default_user=True,
        is_deposit=True,
        is_received=True,
    )

    exceeded_consecutive_deposits: bool = check_consecutive_deposits(
        user_id=1,
        current_activity_event=activity_event,
        concecutive_limit=3,
    )

    assert exceeded_consecutive_deposits is False


@freeze_time("2020-01-01T00:00:00+00:00")
def test_check_consecutive_deposits_when_less_than_limit(
    deposit_activity_events_as_model: list[ActivityEvent],
) -> None:
    db.save(model=deposit_activity_events_as_model[0])

    activity_event: ActivityEvent = ActivityEventFactory(
        is_default_user=True,
        is_deposit=True,
        is_received=True,
    )

    exceeded_consecutive_deposits: bool = check_consecutive_deposits(
        user_id=1,
        current_activity_event=activity_event,
        concecutive_limit=3,
    )

    assert exceeded_consecutive_deposits is False


@freeze_time("2020-01-01T00:00:00+00:00")
def test_check_consecutive_deposits_matches_the_limit(
    deposit_activity_events_as_model: list[ActivityEvent],
) -> None:
    db.save_all(models=deposit_activity_events_as_model[0:1])

    activity_event: ActivityEvent = ActivityEventFactory(
        is_default_user=True,
        is_deposit=True,
        is_received=True,
    )

    exceeded_consecutive_deposits: bool = check_consecutive_deposits(
        user_id=1,
        current_activity_event=activity_event,
        concecutive_limit=3,
    )

    assert exceeded_consecutive_deposits is False


@freeze_time("2020-01-01T00:00:00+00:00")
def test_check_consecutive_deposits_when_exceeding_the_limit_without_increasing_amounts() -> (
    None
):
    db.save_all(
        models=[
            ActivityEventFactory(
                is_default_user=True,
                is_deposit=True,
                is_received=True,
                event_received_at=1577836802,
            ),
            ActivityEventFactory(
                is_default_user=True,
                is_deposit=True,
                is_received=True,
                event_received_at=1577836801,
            ),
        ]
    )

    activity_event: ActivityEvent = ActivityEventFactory(
        is_default_user=True,
        is_deposit=True,
        event_received_at=1577836803,
    )

    exceeded_consecutive_deposits: bool = check_consecutive_deposits(
        user_id=1,
        current_activity_event=activity_event,
        concecutive_limit=3,
    )

    assert exceeded_consecutive_deposits is False


@freeze_time("2020-01-01T00:00:00+00:00")
def test_check_consecutive_deposits_when_exceeding_the_limit_with_increasing_amounts(
    deposit_activity_events_as_model: list[ActivityEvent],
) -> None:
    db.save_all(models=deposit_activity_events_as_model)

    activity_event: ActivityEvent = ActivityEventFactory(
        is_default_user=True,
        is_deposit=True,
        event_received_at=1577836803,
    )

    exceeded_consecutive_deposits: bool = check_consecutive_deposits(
        user_id=1,
        current_activity_event=activity_event,
        concecutive_limit=3,
    )

    assert exceeded_consecutive_deposits is True
