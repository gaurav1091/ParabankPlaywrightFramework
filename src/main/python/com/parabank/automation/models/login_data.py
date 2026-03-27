from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LoginData:
    key: str
    username: str
    password: str

    @classmethod
    def from_dict(cls, data: dict) -> "LoginData":
        return cls(
            key=str(data.get("key", "")).strip(),
            username=str(data.get("username", "")).strip(),
            password=str(data.get("password", "")).strip(),
        )