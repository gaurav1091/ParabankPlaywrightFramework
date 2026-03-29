import os
import re
from pathlib import Path

from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.config.property_reader import PropertyReader


class SensitiveDataResolver:
    _PLACEHOLDER_PATTERN = re.compile(r"\$\{([^}]+)}")
    _local_secrets_cache: dict[str, str] | None = None

    @classmethod
    def resolve_credential_value(cls, raw_value: str | None, context_description: str) -> str:
        resolved_value = cls.resolve_placeholders(raw_value)

        if not resolved_value or cls.contains_placeholder(resolved_value):
            raise RuntimeError(
                f"Sensitive value could not be resolved for: {context_description}. "
                f"Provide it using environment variables, pytest CLI options, "
                f"or {FrameworkConstants.LOCAL_SECRETS_FILE_PATH}."
            )

        return resolved_value.strip()

    @classmethod
    def resolve_placeholders(cls, raw_value: str | None) -> str | None:
        if raw_value is None or not str(raw_value).strip():
            return raw_value

        def replace_match(match: re.Match[str]) -> str:
            placeholder_key = match.group(1).strip()
            replacement = cls.lookup_value(placeholder_key)
            return replacement if replacement is not None else match.group(0)

        return cls._PLACEHOLDER_PATTERN.sub(replace_match, raw_value)

    @classmethod
    def contains_placeholder(cls, value: str | None) -> bool:
        return bool(value and cls._PLACEHOLDER_PATTERN.search(value))

    @classmethod
    def lookup_value(cls, key: str) -> str | None:
        normalized_key = cls.normalize_key(key)

        env_value = os.getenv(normalized_key)
        if env_value and env_value.strip():
            return env_value.strip()

        local_value = cls.get_local_secrets_properties().get(normalized_key)
        if local_value and local_value.strip():
            return local_value.strip()

        return None

    @classmethod
    def normalize_key(cls, key: str) -> str:
        lowered = key.strip().lower()

        if lowered in {"app.username", "username", "parabank_username"}:
            return FrameworkConstants.PARABANK_USERNAME_KEY

        if lowered in {"app.password", "password", "parabank_password"}:
            return FrameworkConstants.PARABANK_PASSWORD_KEY

        if lowered in {"browserstack.username"}:
            return FrameworkConstants.BROWSERSTACK_USERNAME_KEY

        if lowered in {"browserstack.access.key"}:
            return FrameworkConstants.BROWSERSTACK_ACCESS_KEY_KEY

        return key.strip()

    @classmethod
    def get_local_secrets_properties(cls) -> dict[str, str]:
        if cls._local_secrets_cache is None:
            cls._local_secrets_cache = cls.load_local_secrets_properties()
        return cls._local_secrets_cache

    @classmethod
    def load_local_secrets_properties(cls) -> dict[str, str]:
        path = Path(FrameworkConstants.LOCAL_SECRETS_FILE_PATH)

        if not path.exists():
            return {}

        return PropertyReader.load_properties(str(path))
