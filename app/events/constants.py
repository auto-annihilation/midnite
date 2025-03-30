from decimal import Decimal

ACCUMULATIVE_DEPOSIT_AMOUNT_LIMIT: Decimal = Decimal("200.00")
ACCUMULATIVE_DEPOSIT_TIME_LIMIT: int = 30
CONSECUTIVE_DEPOSIT_TRANSACTION_LIMIT: int = 3
CONSECUTIVE_WITHDRAW_TRANSACTION_LIMIT: int = 3
SINGLE_WITHDRAW_AMOUNT_LIMIT: Decimal = Decimal("100.00")
