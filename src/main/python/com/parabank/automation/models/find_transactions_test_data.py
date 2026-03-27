from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FindTransactionsTestData:
    key: str
    amount: str

    @classmethod
    def from_dict(cls, data: dict) -> "FindTransactionsTestData":
        return cls(
            key=str(data.get("key", "")).strip(),
            amount=str(data.get("amount", "")).strip(),
        )