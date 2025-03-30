import logging
import sys
from typing import Any, TextIO

import structlog
from flask import request
from flask.app import Flask
from flask.wrappers import Response

LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "error": logging.ERROR,
}

log: structlog.stdlib.BoundLogger = structlog.get_logger()


def context(**kwargs: Any) -> None:
    _ = structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    structlog.contextvars.clear_contextvars()


def log_inbound_request(response: Response) -> Response:
    log_attrs: dict[str, Any] = {
        "method": request.method,
        "path": request.path,
        "query_string": request.query_string.decode("utf-8"),
        "remote_addr": request.remote_addr,
        "status": response.status_code,
        "user_agent": request.user_agent.to_header(),
        "response_body": response.get_data(as_text=True),
    }

    if request.method in ("PATCH", "POST", "PUT"):
        log_attrs["request_body"] = request.get_data(as_text=True)

    if log_attrs["status"] >= 500:
        log.error("received request", **log_attrs)
    else:
        log.info("received request", **log_attrs)

    return response


def get_renderer(
    format: str,
) -> structlog.processors.JSONRenderer | structlog.dev.ConsoleRenderer:
    if format == "json":
        return structlog.processors.JSONRenderer()

    return structlog.dev.ConsoleRenderer()


class StructlogHandler(logging.StreamHandler):
    """
    Feeds all events back into structlog.
    """

    def __init__(self, stream: TextIO) -> None:
        super().__init__(stream)
        self._log = structlog.get_logger()

    def emit(self, record: logging.LogRecord) -> None:
        # Set _record to allow the add_logger_name processor to identify the
        # correct logger name; otherwise everything is logged as lib.logging.
        self._log.log(
            record.levelno,
            record.getMessage(),
            _record=record,
            exc_info=record.exc_info,
        )


def configure_logger(app: Flask, logger: logging.Logger) -> logging.Logger:
    logger.setLevel(LOG_LEVELS[app.config["LOG_LEVEL"]])
    logger.addHandler(StructlogHandler(sys.stdout))

    # Disable propagation to root logger
    logger.propagate = False

    return logger


def init_app(app: Flask) -> None:
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.disabled = True

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=LOG_LEVELS[app.config["LOG_LEVEL"]],
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
            get_renderer(app.config["LOGFMT"]),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    app.before_request(clear_context)
    app.after_request(log_inbound_request)
