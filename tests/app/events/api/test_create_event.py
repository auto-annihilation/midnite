from decimal import Decimal
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from flask.testing import FlaskClient
from freezegun import freeze_time

from app import db
from app.events.enums import ActivityEventTypeEnum, AlertCodeEnum
from app.events.models import ActivityEvent
from tests.factories.activity_event_factory import ActivityEventFactory

if TYPE_CHECKING:
    from werkzeug.test import TestResponse


@pytest.fixture
def desposit_event_as_dict() -> dict:
    return {"type": "withdraw", "amount": "100.00", "user_id": 1, "t": 0}


@pytest.fixture
def withdraw_event_as_dict() -> dict:
    return {"type": "withdraw", "amount": "100.00", "user_id": 1, "t": 0}


@pytest.fixture
def historic_activity_events_as_model() -> list[ActivityEvent]:
    return [
        ActivityEventFactory(
            is_default_user=True,
            transaction_type=ActivityEventTypeEnum.DEPOSIT,
            amount=Decimal("50.00"),
            is_received=True,
            event_received_at=1577836801,
        ),
        ActivityEventFactory(
            is_default_user=True,
            transaction_type=ActivityEventTypeEnum.DEPOSIT,
            amount=Decimal("75.00"),
            is_received=True,
            event_received_at=1577836802,
        ),
        ActivityEventFactory(
            is_default_user=True,
            is_deposit=True,
            is_received=True,
            event_received_at=1577836803,
        ),
        ActivityEventFactory(
            is_default_user=True,
            is_withdraw=True,
            is_received=True,
            event_received_at=1577836804,
        ),
        ActivityEventFactory(
            is_default_user=True,
            is_withdraw=True,
            is_received=True,
            event_received_at=1577836805,
        ),
    ]


@freeze_time("2020-01-01T00:00:00+00:00")
def test_create_event_for_deposit(
    client: FlaskClient,
    desposit_event_as_dict: dict,
) -> None:
    response: TestResponse = client.post(
        "/event",
        json=desposit_event_as_dict,
        headers=[],
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {
        "alert": False,
        "alert_codes": [],
        "user_id": 1,
    }


@freeze_time("2020-01-01T00:00:00+00:00")
def test_create_event_for_withdraw(
    client: FlaskClient,
    withdraw_event_as_dict: dict,
) -> None:
    response: TestResponse = client.post(
        "/event",
        json=withdraw_event_as_dict,
        headers=[],
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {
        "alert": False,
        "alert_codes": [],
        "user_id": 1,
    }


@freeze_time("2020-01-01T00:00:00+00:00")
def test_create_event_when_withdraw_returns_alert_codes(
    client: FlaskClient,
    historic_activity_events_as_model: list[ActivityEvent],
) -> None:
    db.save_all(models=historic_activity_events_as_model)

    withdraw_event_as_dict: dict = {
        "type": "withdraw",
        "amount": "100.01",
        "user_id": 1,
        "t": 1577836829,
    }

    with freeze_time("2020-01-01T00:00:29+00:00"):
        response: TestResponse = client.post(
            "/event",
            json=withdraw_event_as_dict,
            headers=[],
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {
        "alert": True,
        "alert_codes": [
            AlertCodeEnum.WITHDRAWN_LIMIT_EXCEEDED_CODE.value,
            AlertCodeEnum.CONSECUTIVE_WITHDRAW_CODE.value,
        ],
        "user_id": 1,
    }


@freeze_time("2020-01-01T00:00:00+00:00")
def test_create_event_when_deposit_returns_alert_codes(
    client: FlaskClient,
    historic_activity_events_as_model: list[ActivityEvent],
) -> None:
    db.save_all(models=historic_activity_events_as_model)

    withdraw_event_as_dict: dict = {
        "type": "deposit",
        "amount": "100.01",
        "user_id": 1,
        "t": 1577836829,
    }

    with freeze_time("2020-01-01T00:00:29+00:00"):
        response: TestResponse = client.post(
            "/event",
            json=withdraw_event_as_dict,
            headers=[],
        )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {
        "alert": True,
        "alert_codes": [
            AlertCodeEnum.ACCUMULATIVE_DEPOSIT_CODE.value,
            AlertCodeEnum.CONSECUTIVE_DEPOSIT_CODE.value,
        ],
        "user_id": 1,
    }


@freeze_time("2020-01-01T00:00:00+00:00")
def test_create_event_when_amount_is_zero(
    client: FlaskClient,
) -> None:
    activity_event: dict = {
        "type": "withdraw",
        "amount": "-100.00",
        "user_id": 1,
        "t": 0,
    }

    response: TestResponse = client.post(
        "/event",
        json=activity_event,
        headers=[],
    )

    assert response.status_code == 400
    assert response.json == {
        "error": "Amount must be greater than 0",
    }


@freeze_time("2020-01-01T00:00:00+00:00")
def test_create_event_when_type_unsupported(
    client: FlaskClient,
) -> None:
    activity_event: dict = {
        "type": "balance",
        "amount": "0.00",
        "user_id": 1,
        "t": 0,
    }

    response: TestResponse = client.post(
        "/event",
        json=activity_event,
        headers=[],
    )

    assert response.status_code == 422
    assert response.json == {
        "code": 422,
        "message": str({"type": ["Must be one of: DEPOSIT, WITHDRAW."]}),
    }


@freeze_time("2020-01-01T00:00:00+00:00")
def test_create_event_when_fields_are_missing(
    client: FlaskClient,
) -> None:
    response: TestResponse = client.post(
        "/event",
        json={},
        headers=[],
    )

    assert response.status_code == 422
    assert response.json == {
        "code": 422,
        "message": str(
            {
                "type": ["Missing data for required field."],
                "amount": ["Missing data for required field."],
                "user_id": ["Missing data for required field."],
                "t": ["Missing data for required field."],
            }
        ),
    }
