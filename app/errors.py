import traceback
from http import HTTPStatus

from flask import Blueprint, Response, jsonify
from marshmallow.exceptions import ValidationError
from requests import HTTPError
from werkzeug.exceptions import HTTPException

from app import config

blueprint: Blueprint = Blueprint(name="errors", import_name=__name__)


_STATUS_CODES: dict[type[Exception], int] = {
    ValidationError: 422,
}


@blueprint.app_errorhandler(Exception)
def handle_error(e: Exception) -> tuple[Response, HTTPStatus | int]:
    return jsonify(_build_payload(e)), _map_status(e)


def _build_payload(e: Exception) -> dict:
    message: str = str(e)
    status_code: int = _map_status(e)

    if status_code == 500 and not config.FLASK_DEBUG:
        message = "Something went wrong"

    if config.FLASK_DEBUG:
        return {
            "class": type(e).__name__,
            "message": message,
            "code": _map_status(e),
            "traceback": [
                f"{tb.filename}:{tb.lineno}: {tb.name}"
                for tb in traceback.extract_tb(e.__traceback__)
            ],
        }

    return {"message": message, "code": status_code}


def _map_status(e: Exception) -> HTTPStatus | int:
    if isinstance(e, HTTPException):
        return e.get_response().status_code

    if isinstance(e, HTTPError) and (response := e.response) is not None:
        return response.status_code

    for error_type, status in _STATUS_CODES.items():
        if isinstance(e, error_type):
            return status

    return HTTPStatus.INTERNAL_SERVER_ERROR
