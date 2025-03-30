from typing import Any

import factory
from flask_sqlalchemy.model import DefaultMeta


class SQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session_persistence = None

    @classmethod
    def _create(cls, model_class: DefaultMeta, *args: Any, **kwargs: Any):  # type: ignore[no-untyped-def]
        """Create an instance of the model, and save it to the database."""
        session = cls._meta.sqlalchemy_session

        if session is None:
            raise RuntimeError("No session provided.")

        if cls._meta.sqlalchemy_get_or_create:
            return cls._get_or_create(model_class, session, args, kwargs)

        # overrides the default behaviour which calls `cls._save(model_class, session, args, kwargs)`.
        # `_save()` adds the model instance to a session and then selectively devices to persist or not based on `sqlalchemy_session_persistence`
        # however adding it to the session causes conflicts when running multiple tests using the same fixture.
        # see: https://github.com/FactoryBoy/factory_boy/blob/37f962720814dff42d7a6a848ccfd200fc7f5ae2/factory/alchemy.py#L101-L111
        return model_class(*args, **kwargs)
