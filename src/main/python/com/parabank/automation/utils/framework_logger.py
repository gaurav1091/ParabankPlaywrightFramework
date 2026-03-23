import logging
import logging.config
from pathlib import Path

from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.reports.report_path_manager import ReportPathManager


class FrameworkLogger:
    _configured = False

    @classmethod
    def configure_logging(cls) -> None:
        if cls._configured:
            return

        ReportPathManager.create_directory_if_not_exists(FrameworkConstants.LOGS_FOLDER)

        logging_config_path = Path(FrameworkConstants.LOGGING_CONFIG_FILE)
        if logging_config_path.exists():
            logging.config.fileConfig(logging_config_path, disable_existing_loggers=False)
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            )

        cls._configured = True

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        FrameworkLogger.configure_logging()
        return logging.getLogger(name)