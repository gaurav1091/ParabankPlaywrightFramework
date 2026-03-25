from dataclasses import dataclass
from typing import Any


@dataclass
class CustomerSummary:
    customer_id: int
    first_name: str | None
    last_name: str | None
    username: str | None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "CustomerSummary":
        return CustomerSummary(
            customer_id=int(data["id"]),
            first_name=data.get("firstName"),
            last_name=data.get("lastName"),
            username=data.get("username"),
        )