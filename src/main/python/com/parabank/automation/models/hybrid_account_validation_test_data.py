from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HybridAccountValidationTestData:
    key: str
    login_key: str

    @classmethod
    def from_dict(cls, data: dict) -> "HybridAccountValidationTestData":
        return cls(
            key=str(data.get("key", "")).strip(),
            login_key=str(data.get("loginKey", "")).strip(),
        )
