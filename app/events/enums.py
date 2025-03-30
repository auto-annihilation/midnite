from enum import Enum, auto


class ActivityEventTypeEnum(Enum):
    DEPOSIT = auto()
    WITHDRAW = auto()

    def __str__(self) -> str:
        return self.name.lower()


class AlertCodeEnum(Enum):
    ACCUMULATIVE_DEPOSIT_CODE = 123
    CONSECUTIVE_DEPOSIT_CODE = 300
    CONSECUTIVE_WITHDRAW_CODE = 30
    WITHDRAWN_LIMIT_EXCEEDED_CODE = 1100
