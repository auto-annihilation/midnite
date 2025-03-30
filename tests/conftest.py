from collections.abc import Generator

import pytest
from flask import Flask
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.test import Client

from app import create_app
from app.datastores import (
    SQLAlchemy,
    db as _db,
)


@pytest.fixture(scope="session")
def app() -> Flask:
    return create_app()


@pytest.fixture(autouse=True)
def _setup_app_ctx(app: Flask) -> Generator[None]:
    """Apply application context for every test."""
    with app.app_context():
        yield


@pytest.fixture
def client(app: Flask) -> Client:
    return app.test_client()


@pytest.fixture(scope="session")
def db(app: Flask) -> Generator[SQLAlchemy]:
    """
    Create a database for the duration of the entire testing session
    and drop it in the end of session.
    """

    with app.app_context():
        _db.create_all()

        yield _db

        _db.drop_all()


@pytest.fixture(autouse=True)
def _session(db: SQLAlchemy) -> Generator[None]:
    """Create new scoped session for every test and set it to database's session attribute."""
    connection = db.engine.connect()
    connection.begin()

    session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=connection),
    )
    db.session = session

    yield

    session.rollback()
    connection.close()
