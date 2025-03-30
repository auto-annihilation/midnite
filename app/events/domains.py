from dataclasses import dataclass
from decimal import Decimal

from app.events.enums import ActivityEventTypeEnum


@dataclass
class ActivityEventDomain:
    transaction_type: ActivityEventTypeEnum
    amount: Decimal
    user_id: int
    event_received_at: int


@dataclass
class AlertResponseDomain:
    alert: bool
    alert_codes: list[int]
    user_id: int
