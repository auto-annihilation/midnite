from dataclasses import asdict
from http import HTTPStatus
from typing import TYPE_CHECKING

import structlog
from flask import Blueprint, Response, jsonify, request

from app import db
from app.events.controllers import check_alerts
from app.events.models import ActivityEvent
from app.events.schemas import ActivityEventSchema, AlertResponseSchema
from lib import logging

log: structlog.stdlib.BoundLogger = structlog.get_logger()

if TYPE_CHECKING:
    from app.events.domains import ActivityEventDomain, AlertResponseDomain

routes: Blueprint = Blueprint(
    name="events",
    import_name=__name__,
    url_prefix="/event",
)


@routes.route("", methods=["POST"])
def create_event() -> tuple[Response, HTTPStatus]:
    """Create a new activity event.

    This endpoint accepts POST requests to create an activity event in the system.

    The event data is provided in the request body as JSON.

    Args:
        None

    Returns:
        Response: A tuple containing:
            - JSON response with success message on successful creation (201)
            - JSON response with error message on failure (500)

    Raises:
        500: If there is a database error while saving the event
    """
    logging.context(user_id=request.headers.get("user_id"))

    payload: dict = request.json or {}

    # Note: The source of the `t` which is mapped to event_received_at is not clear from the task description.
    # The assumption is that this is coming from a trusted source and is a Unix epoch timestamp.
    activity_event_as_domain: ActivityEventDomain = ActivityEventSchema().load(payload)

    if activity_event_as_domain.amount <= 0:
        return (
            jsonify({"error": "Amount must be greater than 0"}),
            HTTPStatus.BAD_REQUEST,
        )

    activity_event_as_model: ActivityEvent = ActivityEvent(
        **asdict(activity_event_as_domain)
    )

    alert_response: AlertResponseDomain = check_alerts(
        user_id=activity_event_as_model.user_id,
        current_activity_event=activity_event_as_model,
    )

    log.debug("checking alerts", alert_errors=alert_response.alert_codes)

    # This API identifies alerts and persists events. In a real-world scenario, if there
    # were alerts, preventing the activity may be preferable to allowing it but for the
    # purposes of this task, we will allow the activity to proceed.
    db.save(model=activity_event_as_model)

    log.debug("event created", event_id=activity_event_as_model.id)

    return (
        jsonify(AlertResponseSchema().dump(alert_response)),
        HTTPStatus.CREATED,
    )
