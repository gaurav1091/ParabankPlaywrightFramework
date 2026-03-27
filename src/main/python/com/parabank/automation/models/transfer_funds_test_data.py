from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TransferFundsTestData:
    key: str
    amount: str

    @classmethod
    def from_dict(cls, data: dict) -> "TransferFundsTestData":
        return cls(
            key=str(data.get("key", "")).strip(),
            amount=str(data.get("amount", "")).strip(),
        )