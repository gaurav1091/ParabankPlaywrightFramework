from __future__ import annotations

import shutil
from pathlib import Path

from com.parabank.automation.utils.framework_logger import FrameworkLogger


class ArtifactCleanupManager:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.artifact_cleanup_manager")

    SAFE_ROOT_PREFIXES = (
        "test-output",
    )

    @classmethod
    def cleanup_directories(cls, directories: list[str]) -> None:
        for directory in directories:
            cls.cleanup_directory(directory)

    @classmethod
    def cleanup_directory(cls, directory: str) -> None:
        path = Path(directory).resolve()

        if not cls._is_safe_to_cleanup(path):
            raise ValueError(
                f"Refusing to cleanup unsafe directory path: {path}"
            )

        if path.exists():
            cls.LOGGER.info("Cleaning artifact directory: %s", path)
            shutil.rmtree(path)
        else:
            cls.LOGGER.info("Artifact directory does not exist, skipping cleanup: %s", path)

    @classmethod
    def create_directories(cls, directories: list[str]) -> None:
        for directory in directories:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            cls.LOGGER.info("Ensured artifact directory exists: %s", path)

    @classmethod
    def _is_safe_to_cleanup(cls, path: Path) -> bool:
        normalized = str(path).replace("\\", "/")

        for safe_prefix in cls.SAFE_ROOT_PREFIXES:
            if f"/{safe_prefix}/" in normalized or normalized.endswith(f"/{safe_prefix}") or normalized.endswith(safe_prefix):
                return True

        return False

    @classmethod
    def parse_directories_property(cls, raw_value: str | None) -> list[str]:
        if raw_value is None:
            return []

        directories: list[str] = []

        for entry in raw_value.split(","):
            cleaned = entry.strip()
            if cleaned:
                directories.append(cleaned)

        return directories