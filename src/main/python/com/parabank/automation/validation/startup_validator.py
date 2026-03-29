from pathlib import Path
from urllib.parse import urlparse

import requests

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.exceptions.startup_validation_exception import StartupValidationException
from com.parabank.automation.reports.report_path_manager import ReportPathManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class StartupValidator:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.startup_validator")

    @classmethod
    def validate_or_throw(cls) -> None:
        config_manager = ConfigManager.instance()

        if not config_manager.is_startup_validation_enabled():
            cls.LOGGER.info("Startup validation is disabled by configuration.")
            cls.validate_report_directories()
            return

        cls.validate_environment(config_manager.get_current_environment())
        cls.validate_browser(config_manager.get_browser())
        cls.validate_execution_mode(config_manager.get_execution_mode())
        cls.validate_uri("base.url", config_manager.get_base_url())
        cls.validate_uri("api.base.url", config_manager.get_api_base_url())

        if config_manager.is_remote_execution():
            cls.validate_remote_provider(config_manager.get_remote_provider())

            if config_manager.is_browserstack_execution():
                cls.validate_uri("browserstack.hub.url", config_manager.get_browserstack_hub_url())
                cls.validate_non_blank("browserstack.username", config_manager.get_browserstack_username())
                cls.validate_non_blank("browserstack.access.key", config_manager.get_browserstack_access_key())
                cls.validate_non_blank("browserstack.os", config_manager.get_browserstack_os())
                cls.validate_non_blank("browserstack.os.version", config_manager.get_browserstack_os_version())
                cls.validate_non_blank(
                    "browserstack.browser.version",
                    config_manager.get_browserstack_browser_version(),
                )

        cls.validate_positive("implicit.wait", config_manager.get_implicit_wait())
        cls.validate_positive("explicit.wait", config_manager.get_explicit_wait())
        cls.validate_positive("page.load.timeout", config_manager.get_page_load_timeout())
        cls.validate_positive("script.timeout", config_manager.get_script_timeout())

        cls.validate_parallel_settings(config_manager)

        cls.validate_non_negative("retry.count", config_manager.get_retry_count())
        cls.validate_non_negative("retry.delay.seconds", config_manager.get_retry_delay_seconds())
        cls.validate_positive(
            "api.connect.timeout.seconds",
            config_manager.get_api_connect_timeout_seconds(),
        )
        cls.validate_positive(
            "api.read.timeout.seconds",
            config_manager.get_api_read_timeout_seconds(),
        )
        cls.validate_positive(
            "startup.validation.timeout.seconds",
            config_manager.get_startup_validation_timeout_seconds(),
        )

        cls.validate_endpoint_reachability(
            "Application Base URL",
            config_manager.get_base_url(),
            config_manager.get_startup_validation_timeout_seconds(),
        )
        cls.validate_endpoint_reachability(
            "API Base URL",
            config_manager.get_api_base_url(),
            config_manager.get_startup_validation_timeout_seconds(),
        )

        cls.validate_report_directories()
        cls.LOGGER.info("Startup validation completed successfully.")

    @classmethod
    def validate_environment(cls, environment: str) -> None:
        if environment not in FrameworkConstants.SUPPORTED_ENVIRONMENTS:
            raise StartupValidationException("Invalid environment configuration. Supported values: qa, stage, dev.")
        cls.LOGGER.info("Validated environment: %s", environment)

    @classmethod
    def validate_browser(cls, browser: str) -> None:
        if not browser or browser.strip().lower() not in FrameworkConstants.SUPPORTED_BROWSERS:
            raise StartupValidationException(
                f"Unsupported browser configured: {browser}. " f"Supported values: chrome, firefox, edge."
            )
        cls.LOGGER.info("Validated browser: %s", browser.strip().lower())

    @classmethod
    def validate_execution_mode(cls, execution_mode: str) -> None:
        if not execution_mode or execution_mode.strip().lower() not in FrameworkConstants.SUPPORTED_EXECUTION_MODES:
            raise StartupValidationException(
                f"Unsupported execution mode: {execution_mode}. " f"Supported values: local, remote."
            )
        cls.LOGGER.info("Validated execution mode: %s", execution_mode.strip().lower())

    @classmethod
    def validate_remote_provider(cls, remote_provider: str) -> None:
        if not remote_provider or remote_provider.strip().lower() != "browserstack":
            raise StartupValidationException(
                f"Unsupported remote provider: {remote_provider}. " f"Supported value: browserstack."
            )
        cls.LOGGER.info("Validated remote provider: %s", remote_provider.strip().lower())

    @classmethod
    def validate_parallel_settings(cls, config_manager: ConfigManager) -> None:
        cls.validate_positive("thread.count", config_manager.get_thread_count())
        cls.validate_positive(
            "data.provider.thread.count",
            config_manager.get_data_provider_thread_count(),
        )

        parallel_mode = config_manager.get_parallel_mode()
        if parallel_mode not in FrameworkConstants.SUPPORTED_PARALLEL_MODES:
            raise StartupValidationException(
                f"Unsupported parallel.mode: {parallel_mode}. "
                f"Supported values: {sorted(FrameworkConstants.SUPPORTED_PARALLEL_MODES)}"
            )

        cls.LOGGER.info("Validated parallel.mode: %s", parallel_mode)

        parallel_dist_mode = config_manager.get_parallel_dist_mode()
        if parallel_dist_mode not in FrameworkConstants.SUPPORTED_XDIST_DIST_MODES:
            raise StartupValidationException(
                f"Unsupported parallel.dist.mode: {parallel_dist_mode}. "
                f"Supported values: {sorted(FrameworkConstants.SUPPORTED_XDIST_DIST_MODES)}"
            )

        cls.LOGGER.info("Validated parallel.dist.mode: %s", parallel_dist_mode)

        serial_marker_name = config_manager.get_serial_marker_name()
        cls.validate_non_blank("serial.marker.name", serial_marker_name)

        cls.LOGGER.info(
            "Validated parallel settings. enabled=%s | thread.count=%s | data.provider.thread.count=%s | serial.marker.name=%s",
            config_manager.is_parallel_enabled(),
            config_manager.get_thread_count(),
            config_manager.get_data_provider_thread_count(),
            serial_marker_name,
        )

    @classmethod
    def validate_uri(cls, property_name: str, uri_value: str) -> None:
        if not uri_value or not uri_value.strip():
            raise StartupValidationException(f"Required configuration is missing: {property_name}")

        parsed = urlparse(uri_value.strip())
        if not parsed.scheme or not parsed.netloc:
            raise StartupValidationException(f"Invalid URI configured for {property_name}: {uri_value}")

        cls.LOGGER.info("Validated URI for property: %s", property_name)

    @classmethod
    def validate_non_blank(cls, property_name: str, value: str) -> None:
        if not value or not value.strip():
            raise StartupValidationException(f"Required configuration is missing: {property_name}")

        cls.LOGGER.info("Validated non-blank configuration: %s", property_name)

    @classmethod
    def validate_positive(cls, property_name: str, value: int) -> None:
        if value <= 0:
            raise StartupValidationException(
                f"Configuration value must be greater than zero for property: " f"{property_name} | Actual: {value}"
            )

        cls.LOGGER.info("Validated positive numeric configuration: %s=%s", property_name, value)

    @classmethod
    def validate_non_negative(cls, property_name: str, value: int) -> None:
        if value < 0:
            raise StartupValidationException(
                f"Configuration value must be zero or greater for property: " f"{property_name} | Actual: {value}"
            )

        cls.LOGGER.info("Validated non-negative numeric configuration: %s=%s", property_name, value)

    @classmethod
    def validate_endpoint_reachability(
        cls,
        endpoint_name: str,
        url: str,
        timeout_seconds: int,
    ) -> None:
        try:
            response = requests.get(url, timeout=timeout_seconds)
            cls.LOGGER.info(
                "Validated endpoint reachability: %s -> HTTP %s",
                endpoint_name,
                response.status_code,
            )
        except Exception as exc:
            raise StartupValidationException(
                f"Failed startup reachability validation for {endpoint_name} at URL: {url}"
            ) from exc

    @classmethod
    def validate_report_directories(cls) -> None:
        try:
            ReportPathManager.create_directory_if_not_exists(FrameworkConstants.REPORTS_FOLDER)
            ReportPathManager.create_directory_if_not_exists(FrameworkConstants.SCREENSHOTS_FOLDER)
            ReportPathManager.create_directory_if_not_exists(FrameworkConstants.CUCUMBER_REPORTS_FOLDER)
            ReportPathManager.create_directory_if_not_exists(FrameworkConstants.LOGS_FOLDER)
            ReportPathManager.create_directory_if_not_exists(FrameworkConstants.TRACES_FOLDER)
            ReportPathManager.create_directory_if_not_exists(FrameworkConstants.VIDEOS_FOLDER)

            framework_log_path = Path(FrameworkConstants.LOGS_FOLDER) / "framework_master.log"
            if not framework_log_path.exists():
                framework_log_path.touch(exist_ok=True)

        except Exception as exc:
            raise StartupValidationException("Failed to create or validate report directories.") from exc

        cls.LOGGER.info("Validated report/artifact directories.")
