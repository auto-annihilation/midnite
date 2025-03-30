from typing import TypeVar

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from flask_sqlalchemy.model import Model
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    scoped_session,
)

from app import config

_BaseModelT = TypeVar("_BaseModelT", bound=Model)


class SQLAlchemy(_SQLAlchemy):
    session: scoped_session

    def init_app(self, app: Flask) -> None:
        super().init_app(app)
        Migrate(app, self)

    def save(self, model: _BaseModelT) -> Model:
        try:
            self.session.add(model)
            self.session.commit()
            return model
        except IntegrityError:
            self.session.rollback()
            raise

    def save_all(self, models: list[_BaseModelT]) -> list[_BaseModelT]:
        try:
            for model in models:
                self.session.add(model)
            self.session.commit()

            return models
        except IntegrityError:
            self.session.rollback()
            raise


db: SQLAlchemy = SQLAlchemy(
    engine_options=config.SQLALCHEMY_ENGINE_OPTIONS,
)
