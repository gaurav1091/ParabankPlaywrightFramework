from __future__ import annotations

from dataclasses import dataclass

from com.parabank.automation.config.sensitive_data_resolver import SensitiveDataResolver


@dataclass
class LoginData:
    key: str
    username: str
    password: str

    @staticmethod
    def _resolve_value(raw_value: object) -> str:
        value = "" if raw_value is None else str(raw_value).strip()
        resolved_value = SensitiveDataResolver.resolve_placeholders(value)
        return "" if resolved_value is None else str(resolved_value).strip()

    @classmethod
    def from_dict(cls, data: dict) -> "LoginData":
        return cls(
            key=str(data.get("key", "")).strip(),
            username=cls._resolve_value(data.get("username", "")),
            password=cls._resolve_value(data.get("password", "")),
        )