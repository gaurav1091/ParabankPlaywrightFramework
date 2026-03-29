import configparser
import logging
import logging.config
import os
from pathlib import Path

from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.reports.report_path_manager import ReportPathManager


class FrameworkLogger:
    _configured = False

    @classmethod
    def _get_worker_id(cls) -> str:
        worker_id = os.getenv("PYTEST_XDIST_WORKER", "").strip()
        if worker_id:
            return worker_id
        return "master"

    @classmethod
    def _get_worker_log_file_path(cls) -> Path:
        worker_id = cls._get_worker_id()
        return Path(FrameworkConstants.LOGS_FOLDER) / f"framework_{worker_id}.log"

    @classmethod
    def configure_logging(cls) -> None:
        if cls._configured:
            return

        ReportPathManager.create_directory_if_not_exists(FrameworkConstants.LOGS_FOLDER)

        logging_config_path = Path(FrameworkConstants.LOGGING_CONFIG_FILE)
        worker_log_file_path = cls._get_worker_log_file_path()

        if logging_config_path.exists():
            parser = configparser.ConfigParser()
            parser.read(logging_config_path, encoding="utf-8")

            if parser.has_section("handler_fileHandler"):
                parser.set(
                    "handler_fileHandler",
                    "args",
                    f"('{worker_log_file_path.as_posix()}', 'a', 'utf-8')",
                )

            logging.config.fileConfig(parser, disable_existing_loggers=False)
        else:
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)

            formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")

            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)

            file_handler = logging.FileHandler(worker_log_file_path, mode="a", encoding="utf-8")
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)

            root_logger.handlers.clear()
            root_logger.addHandler(console_handler)
            root_logger.addHandler(file_handler)

        cls._configured = True

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        FrameworkLogger.configure_logging()
        return logging.getLogger(name)
