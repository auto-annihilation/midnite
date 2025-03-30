from freezegun import freeze_time

from app import db
from app.events.controllers import check_consecutive_withdraws
from app.events.models import ActivityEvent
from tests.factories.activity_event_factory import ActivityEventFactory


@freeze_time("2020-01-01T00:00:00+00:00")
def test_check_consecutive_withdraws_when_no_history_exists() -> None:
    activity_event: ActivityEvent = ActivityEventFactory(
        is_default_user=True,
        is_deposit=True,
        is_received=True,
    )

    exceeded_consecutive_withdraws: bool = check_consecutive_withdraws(
        user_id=1,
        current_activity_event=activity_event,
        concecutive_limit=3,
    )

    assert exceeded_consecutive_withdraws is False


@freeze_time("2020-01-01T00:00:00+00:00")
def test_check_consecutive_withdraws_when_withing_the_limit(
    withdraw_activity_events_as_model: list[ActivityEvent],
) -> None:
    db.save_all(models=withdraw_activity_events_as_model[0:1])

    activity_event: ActivityEvent = ActivityEventFactory(
        is_default_user=True,
        is_withdraw=True,
        is_received=True,
    )

    exceeded_consecutive_withdraws: bool = check_consecutive_withdraws(
        user_id=1,
        current_activity_event=activity_event,
        concecutive_limit=3,
    )

    assert exceeded_consecutive_withdraws is False


@freeze_time("2020-01-01T00:00:00+00:00")
def test_check_consecutive_withdraws_when_exceeding_the_limit(
    withdraw_activity_events_as_model: list[ActivityEvent],
) -> None:
    db.save_all(models=withdraw_activity_events_as_model)

    activity_event: ActivityEvent = ActivityEventFactory(
        user_id=1,
        is_default_user=True,
        is_withdraw=True,
        is_received=True,
    )

    exceeded_consecutive_withdraws: bool = check_consecutive_withdraws(
        user_id=1,
        current_activity_event=activity_event,
        concecutive_limit=3,
    )

    assert exceeded_consecutive_withdraws is True
