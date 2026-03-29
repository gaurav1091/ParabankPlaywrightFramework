import json
from pathlib import Path

from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class JsonReader:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.json_reader")

    @staticmethod
    def _build_full_path(relative_path: str) -> Path:
        return Path(FrameworkConstants.TEST_DATA_RESOURCES_ROOT) / relative_path

    @classmethod
    def read_json(cls, relative_path: str) -> dict:
        file_path = cls._build_full_path(relative_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Test data file not found: {file_path}")

        cls.LOGGER.info("Reading JSON test data file: %s", file_path)

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def read_json_by_key(cls, relative_path: str, key: str) -> dict:
        data = cls.read_json(relative_path)

        if key not in data:
            raise KeyError(f"Key '{key}' not found in JSON file: {relative_path}")

        return data[key]
