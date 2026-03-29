from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OpenNewAccountTestData:
    key: str
    account_type: str

    @classmethod
    def from_dict(cls, data: dict) -> "OpenNewAccountTestData":
        return cls(
            key=str(data.get("key", "")).strip(),
            account_type=str(data.get("accountType", "")).strip(),
        )
