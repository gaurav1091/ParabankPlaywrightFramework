from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HybridUiToApiAccountCreationTestData:
    key: str
    login_key: str
    open_new_account_key: str

    @classmethod
    def from_dict(cls, data: dict) -> "HybridUiToApiAccountCreationTestData":
        return cls(
            key=str(data.get("key", "")).strip(),
            login_key=str(data.get("loginKey", "")).strip(),
            open_new_account_key=str(data.get("openNewAccountKey", "")).strip(),
        )