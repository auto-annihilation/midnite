from app.events.domains import ActivityEventDomain, AlertResponseDomain
from app.events.enums import ActivityEventTypeEnum
from lib import fields
from lib.schemas import BaseSchema


class ActivityEventSchema(BaseSchema[ActivityEventDomain]):
    transaction_type = fields.CaseInsensitiveEnum(
        ActivityEventTypeEnum, required=True, data_key="type"
    )
    amount = fields.Decimal(required=True)
    user_id = fields.Integer(required=True)

    # NOTE: The field `t` maps to event_received_at and represents a Unix epoch timestamp.
    # While this naming aligns with the API contract, a more descriptive field name
    # in future API versions would help improve clarity and maintainability.
    event_received_at = fields.Integer(required=True, data_key="t")


class AlertResponseSchema(BaseSchema[AlertResponseDomain]):
    alert = fields.Boolean(required=True)
    alert_codes = fields.List(fields.Integer(), required=True)
    user_id = fields.Integer(required=True)
