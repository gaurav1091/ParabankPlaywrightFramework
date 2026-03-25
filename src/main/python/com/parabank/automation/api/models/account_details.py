from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass
class AccountDetails:
    account_id: int
    customer_id: int | None
    account_type: str | None
    balance: Decimal | None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "AccountDetails":
        balance_value = data.get("balance")
        normalized_balance = Decimal(str(balance_value)) if balance_value is not None else None

        return AccountDetails(
            account_id=int(data["id"]),
            customer_id=int(data["customerId"]) if data.get("customerId") is not None else None,
            account_type=data.get("type"),
            balance=normalized_balance,
        )