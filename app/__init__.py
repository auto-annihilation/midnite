from flask import Flask
from flask_cors import CORS

from app import config
from app.datastores import db
from app.errors import blueprint as error_handler
from app.events import api as events_api
from lib import logging

ALLOWED_ORIGINS = {
    "development": ["http://localhost:*"],
    "test": ["*"],
}


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object("app.config")

    CORS(app, origins=ALLOWED_ORIGINS.get(config.SERVICE_ENV))  # type: ignore[arg-type]

    # Routes
    app.register_blueprint(blueprint=events_api.routes)

    # Error handling
    app.register_blueprint(blueprint=error_handler)

    # Initialise logging
    logging.init_app(app=app)

    # Initialise database
    db.init_app(app=app)

    return app
