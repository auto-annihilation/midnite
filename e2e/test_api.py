from datetime import datetime
from http import HTTPStatus

import pytest
import requests


@pytest.fixture()
def base_url() -> str:
    return "http://web:5000"


@pytest.fixture()
def headers() -> dict[str, str]:
    return {"Content-Type": "application/json"}


@pytest.fixture()
def user_id() -> int:
    """Ensures user_id is unique on each test run by using "
    the epoch timestamp + millisecond precision."
    """
    return int(datetime.now().timestamp() * 1000000)


@pytest.fixture()
def epoch_now() -> int:
    return int(datetime.now().timestamp())


def act_and_assert(
    activity_events: list[dict], base_url: str, headers: dict[str, str]
) -> list[dict]:
    """A utility helper function for making POST requests and validating responses are successful.

    Returns:
        list[dict]: A list of JSON responses from the POST requests
    """
    responses: list[dict] = []

    for data in activity_events:
        response = requests.post(
            f"{base_url}/event",
            headers=headers,
            json=data,
            timeout=1,
        )
        responses.append(response.json())
        assert response.status_code == HTTPStatus.CREATED

    return responses


def test_withdraw_over_100(
    base_url: str,
    headers: dict[str, str],
    user_id: int,
    epoch_now: int,
) -> None:
    activity_events: list[dict] = [
        {
            "type": "withdraw",
            "amount": "100.00",
            "user_id": user_id,
            "t": epoch_now - 30,
        },
        {
            "type": "withdraw",
            "amount": "100.01",
            "user_id": user_id,
            "t": epoch_now - 29,
        },
    ]

    responses: list[dict] = act_and_assert(
        activity_events=activity_events,
        base_url=base_url,
        headers=headers,
    )

    assert len(responses) == 2
    assert responses == [
        {
            "alert": False,
            "alert_codes": [],
            "user_id": user_id,
        },
        {
            "alert": True,
            "alert_codes": [1100],
            "user_id": user_id,
        },
    ]


def test_consecutive_withdraws(
    base_url: str,
    headers: dict[str, str],
    user_id: int,
    epoch_now: int,
) -> None:
    activity_events: list[dict] = [
        {
            "type": "withdraw",
            "amount": "100.00",
            "user_id": user_id,
            "t": epoch_now - 30,
        },
        {
            "type": "withdraw",
            "amount": "100.00",
            "user_id": user_id,
            "t": epoch_now - 29,
        },
        {
            "type": "withdraw",
            "amount": "100.00",
            "user_id": user_id,
            "t": epoch_now - 28,
        },
    ]

    responses: list[dict] = act_and_assert(
        activity_events=activity_events,
        base_url=base_url,
        headers=headers,
    )

    assert len(responses) == 3
    assert responses == [
        {
            "alert": False,
            "alert_codes": [],
            "user_id": user_id,
        },
        {
            "alert": False,
            "alert_codes": [],
            "user_id": user_id,
        },
        {
            "alert": True,
            "alert_codes": [30],
            "user_id": user_id,
        },
    ]


def test_consecutive_deposits_exceeding_30_seconds(
    base_url: str,
    headers: dict[str, str],
    user_id: int,
    epoch_now: int,
) -> None:
    activity_events: list[dict] = [
        {
            "type": "deposit",
            "amount": "50.00",
            "user_id": user_id,
            "t": epoch_now - 31,
        },
        {
            "type": "deposit",
            "amount": "75.00",
            "user_id": user_id,
            "t": epoch_now - 29,
        },
        {
            "type": "withdraw",
            "amount": "100.00",
            "user_id": user_id,
            "t": epoch_now - 28,
        },
        {
            "type": "deposit",
            "amount": "100.00",
            "user_id": user_id,
            "t": epoch_now - 27,
        },
    ]

    responses: list[dict] = act_and_assert(
        activity_events=activity_events,
        base_url=base_url,
        headers=headers,
    )

    assert len(responses) == 4
    assert responses == [
        {
            "alert": False,
            "alert_codes": [],
            "user_id": user_id,
        },
        {
            "alert": False,
            "alert_codes": [],
            "user_id": user_id,
        },
        {
            "alert": False,
            "alert_codes": [],
            "user_id": user_id,
        },
        {
            "alert": True,
            "alert_codes": [300],
            "user_id": user_id,
        },
    ]


def test_accumulative_deposits_within_30_seconds(
    base_url: str,
    headers: dict[str, str],
    user_id: int,
    epoch_now: int,
) -> None:
    activity_events: list[dict] = [
        {
            "type": "deposit",
            "amount": "50.00",
            "user_id": user_id,
            "t": epoch_now - 30,
        },
        {
            "type": "deposit",
            "amount": "75.00",
            "user_id": user_id,
            "t": epoch_now - 29,
        },
        {
            "type": "withdraw",
            "amount": "100.00",
            "user_id": user_id,
            "t": epoch_now - 28,
        },
        {
            "type": "deposit",
            "amount": "100.00",
            "user_id": user_id,
            "t": epoch_now - 27,
        },
    ]

    responses: list[dict] = act_and_assert(
        activity_events=activity_events,
        base_url=base_url,
        headers=headers,
    )

    assert len(responses) == 4
    assert responses == [
        {
            "alert": False,
            "alert_codes": [],
            "user_id": user_id,
        },
        {
            "alert": False,
            "alert_codes": [],
            "user_id": user_id,
        },
        {
            "alert": False,
            "alert_codes": [],
            "user_id": user_id,
        },
        {
            "alert": True,
            "alert_codes": [123, 300],
            "user_id": user_id,
        },
    ]
