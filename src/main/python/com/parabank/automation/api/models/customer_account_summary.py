from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass
class CustomerAccountSummary:
    account_id: int
    account_type: str | None
    balance: Decimal | None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "CustomerAccountSummary":
        balance_value = data.get("balance")
        normalized_balance = Decimal(str(balance_value)) if balance_value is not None else None

        return CustomerAccountSummary(
            account_id=int(data["id"]),
            account_type=data.get("type"),
            balance=normalized_balance,
        )