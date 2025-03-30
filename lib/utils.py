from datetime import UTC, datetime
from uuid import UUID, uuid4


def get_uuid() -> UUID:
    """Produces a string uuid4 when provided as the default value within
    a SQLAlchemy model.
    """
    return uuid4()


def get_utc_now() -> datetime:
    """Produces the current datetime as UTC when provided as a default within
    a SQLAlchemy model. Also used to freeze datetime via freezegun during testing.
    """
    return datetime.now(tz=UTC)


def get_epoch_now() -> int:
    """Produces the current time in epoch format."""
    return int(datetime.now().timestamp())
