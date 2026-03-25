import json
from pathlib import Path
from typing import List

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.models.login_data import LoginData
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class DataProvider:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.data_provider")

    @classmethod
    def _resolve_file_path(cls, relative_path: str) -> Path:
        base_path = ConfigManager.instance().get_test_data_base_path()
        full_path = Path(base_path) / relative_path

        cls.LOGGER.info("Resolved test data file path: %s", full_path)

        if not full_path.exists():
            raise FileNotFoundError(f"Test data file not found: {full_path}")

        return full_path

    @classmethod
    def _read_json(cls, relative_path: str) -> dict:
        file_path = cls._resolve_file_path(relative_path)

        cls.LOGGER.info("Reading JSON test data file: %s", file_path)

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def get_login_data(cls, relative_path: str, key: str) -> LoginData:
        data = cls._read_json(relative_path)

        if key not in data:
            raise KeyError(f"Key '{key}' not found in test data file: {relative_path}")

        return LoginData.from_dict(data[key])

    @classmethod
    def get_all_login_data(cls, relative_path: str) -> List[LoginData]:
        data = cls._read_json(relative_path)

        return [LoginData.from_dict(value) for value in data.values()]