from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import factory

from app import db
from app.events.enums import ActivityEventTypeEnum
from app.events.models import ActivityEvent
from lib.factory import SQLAlchemyModelFactory


class ActivityEventFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ActivityEvent
        sqlalchemy_session = db.session

    id = None
    user_id = None
    created_at = None
    updated_at = None
    transaction_type = None
    amount = None
    event_received_at = None

    class Params:
        is_persisted = factory.Trait(
            id=uuid4(),
            created_at=datetime(
                year=2021, month=1, day=1, hour=0, minute=0, second=0, tzinfo=UTC
            ),
            updated_at=datetime(
                year=2021, month=1, day=1, hour=0, minute=0, second=0, tzinfo=UTC
            ),
        )

        is_default_user = factory.Trait(user_id=1)

        is_received = factory.Trait(
            event_received_at=1577836799,
        )

        is_deposit = factory.Trait(
            transaction_type=ActivityEventTypeEnum.DEPOSIT,
            amount=Decimal("100.00"),
        )

        is_withdraw = factory.Trait(
            transaction_type=ActivityEventTypeEnum.WITHDRAW,
            amount=Decimal("100.00"),
        )
