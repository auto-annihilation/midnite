import functools
from typing import Any

from marshmallow import fields

# Adjust the defaults for marshmallow fields to provide sensible defaults
Boolean = functools.partial(fields.Boolean, allow_none=False, required=True)
DateTime = functools.partial(fields.DateTime, allow_none=False, required=True)
Decimal = functools.partial(
    fields.Decimal, allow_none=False, required=True, places=2, as_string=True
)
Integer = functools.partial(fields.Integer, allow_none=False, required=True)
List = functools.partial(fields.List, allow_none=False, required=True)
Nested = functools.partial(fields.Nested, allow_none=False, required=True)
String = functools.partial(fields.String, allow_none=False, required=True)
UUID = functools.partial(fields.UUID, allow_none=False, required=True)


class CaseInsensitiveEnum(fields.Enum):
    """
    Field converts value to lowercase string during serialization and
    to uppercase during deserialization.
    """

    def _serialize(self, value: Any, attr: str | None, obj: Any, **kwargs: Any) -> Any:
        serialized_value = super()._serialize(value, attr, obj, **kwargs)

        if isinstance(serialized_value, str):
            return serialized_value.lower()

        return None

    def _deserialize(
        self, value: Any, attr: str | None, data: Any, **kwargs: Any
    ) -> Any:
        return super()._deserialize(value.upper(), attr, data, **kwargs)
