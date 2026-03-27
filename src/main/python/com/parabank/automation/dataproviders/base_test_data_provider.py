from __future__ import annotations

from typing import Callable, TypeVar

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger
from com.parabank.automation.utils.json_reader import JsonReader


T = TypeVar("T")


class BaseTestDataProvider:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.base_test_data_provider")

    @classmethod
    def _resolve_relative_path_for_current_env(cls, file_name: str) -> str:
        current_env = ConfigManager.instance().get_current_environment()
        relative_path = f"{current_env}/{file_name}"
        cls.LOGGER.info("Resolved environment-aware test data path: %s", relative_path)
        return relative_path

    @classmethod
    def _load_list_json(cls, file_name: str) -> list[dict]:
        relative_path = cls._resolve_relative_path_for_current_env(file_name)
        data = JsonReader.read_json(relative_path)

        if not isinstance(data, list):
            raise AssertionError(
                f"Expected list-based JSON test data in file '{relative_path}', "
                f"but found: {type(data).__name__}"
            )

        return data

    @classmethod
    def get_test_data_by_key(
        cls,
        file_name: str,
        key: str,
        mapper: Callable[[dict], T],
    ) -> T:
        records = cls._load_list_json(file_name)

        for record in records:
            if str(record.get("key", "")).strip() == key:
                cls.LOGGER.info(
                    "Matched JSON test data record. File=%s | Key=%s",
                    file_name,
                    key,
                )
                return mapper(record)

        raise KeyError(f"Key '{key}' not found in JSON test data file '{file_name}'")