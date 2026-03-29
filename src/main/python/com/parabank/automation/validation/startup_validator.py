from __future__ import annotations

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
            return

        cls.LOGGER.info("Running startup validation.")

        cls.validate_environment(config_manager)
        cls.validate_browser(config_manager)
        cls.validate_execution_mode(config_manager)
        cls.validate_application_urls(config_manager)
        cls.validate_timeouts(config_manager)
        cls.validate_retry_settings(config_manager)
        cls.validate_parallel_settings(config_manager)
        cls.validate_required_directories()

        cls.LOGGER.info("Startup validation completed successfully.")

    @classmethod
    def validate_environment(cls, config_manager: ConfigManager) -> None:
        current_environment = config_manager.get_current_environment()
        if current_environment not in FrameworkConstants.SUPPORTED_ENVIRONMENTS:
            raise StartupValidationException(
                f"Unsupported environment configured: {current_environment}. "
                f"Supported values: {sorted(FrameworkConstants.SUPPORTED_ENVIRONMENTS)}"
            )

        cls.LOGGER.info("Validated environment: %s", current_environment)

    @classmethod
    def validate_browser(cls, config_manager: ConfigManager) -> None:
        browser_name = config_manager.get_browser()
        if browser_name not in FrameworkConstants.SUPPORTED_BROWSERS:
            raise StartupValidationException(
                f"Unsupported browser configured: {browser_name}. "
                f"Supported values: {sorted(FrameworkConstants.SUPPORTED_BROWSERS)}"
            )

        cls.LOGGER.info("Validated browser: %s", browser_name)

    @classmethod
    def validate_execution_mode(cls, config_manager: ConfigManager) -> None:
        execution_mode = config_manager.get_execution_mode()
        if execution_mode not in FrameworkConstants.SUPPORTED_EXECUTION_MODES:
            raise StartupValidationException(
                f"Unsupported execution.mode: {execution_mode}. "
                f"Supported values: {sorted(FrameworkConstants.SUPPORTED_EXECUTION_MODES)}"
            )

        cls.LOGGER.info("Validated execution.mode: %s", execution_mode)

        if execution_mode == "remote":
            remote_provider = config_manager.get_remote_provider()
            if remote_provider not in FrameworkConstants.SUPPORTED_REMOTE_PROVIDERS:
                raise StartupValidationException(
                    f"Unsupported remote.provider: {remote_provider}. "
                    f"Supported values: {sorted(FrameworkConstants.SUPPORTED_REMOTE_PROVIDERS)}"
                )

            cls.LOGGER.info("Validated remote.provider: %s", remote_provider)

    @classmethod
    def validate_application_urls(cls, config_manager: ConfigManager) -> None:
        cls.validate_uri("base.url", config_manager.get_base_url())
        cls.validate_uri("api.base.url", config_manager.get_api_base_url())

    @classmethod
    def validate_timeouts(cls, config_manager: ConfigManager) -> None:
        cls.validate_positive("default.timeout.millis", config_manager.get_default_timeout_millis())
        cls.validate_positive("page.load.timeout.millis", config_manager.get_page_load_timeout_millis())
        cls.validate_positive(
            "playwright.action.timeout.millis",
            config_manager.get_playwright_action_timeout_millis(),
        )
        cls.validate_positive(
            "playwright.navigation.timeout.millis",
            config_manager.get_playwright_navigation_timeout_millis(),
        )
        cls.validate_positive("api.connect.timeout.seconds", config_manager.get_api_connect_timeout_seconds())
        cls.validate_positive("api.read.timeout.seconds", config_manager.get_api_read_timeout_seconds())

    @classmethod
    def validate_retry_settings(cls, config_manager: ConfigManager) -> None:
        cls.validate_non_negative("retry.count", config_manager.get_retry_count())
        cls.validate_non_negative("retry.delay.seconds", config_manager.get_retry_delay_seconds())

    @classmethod
    def validate_parallel_settings(cls, config_manager: ConfigManager) -> None:
        thread_count = config_manager.get_thread_count()
        data_provider_thread_count = config_manager.get_data_provider_thread_count()

        cls.validate_positive("thread.count", thread_count)
        cls.validate_positive("data.provider.thread.count", data_provider_thread_count)

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
            (
                "Validated parallel settings. enabled=%s | thread.count=%s | "
                "data.provider.thread.count=%s | serial.marker.name=%s"
            ),
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
            raise StartupValidationException(f"Configuration value must be greater than zero. {property_name}={value}")

        cls.LOGGER.info("Validated positive numeric configuration: %s=%s", property_name, value)

    @classmethod
    def validate_non_negative(cls, property_name: str, value: int) -> None:
        if value < 0:
            raise StartupValidationException(f"Configuration value cannot be negative. {property_name}={value}")

        cls.LOGGER.info("Validated non-negative numeric configuration: %s=%s", property_name, value)

    @classmethod
    def validate_required_directories(cls) -> None:
        required_directories = [
            FrameworkConstants.REPORTS_FOLDER,
            FrameworkConstants.SCREENSHOTS_FOLDER,
            FrameworkConstants.CUCUMBER_REPORTS_FOLDER,
            FrameworkConstants.LOGS_FOLDER,
            FrameworkConstants.TRACES_FOLDER,
            FrameworkConstants.VIDEOS_FOLDER,
            "test-output/allure-results",
            "test-output/reports/images",
        ]

        for directory in required_directories:
            ReportPathManager.create_directory_if_not_exists(directory)

            if not Path(directory).exists():
                raise StartupValidationException(
                    f"Required artifact directory is missing and could not be created: {directory}"
                )

        cls.LOGGER.info("Validated required artifact directories successfully.")

    @classmethod
    def validate_application_reachability(cls, config_manager: ConfigManager) -> None:
        if not config_manager.is_startup_validation_enabled():
            return

        base_url = config_manager.get_base_url()

        try:
            response = requests.get(
                base_url,
                timeout=config_manager.get_api_connect_timeout_seconds(),
                verify=False,
            )
            cls.LOGGER.info(
                "Application reachability check completed. URL=%s | Status=%s",
                base_url,
                response.status_code,
            )
        except requests.RequestException as exc:
            raise StartupValidationException(f"Application reachability validation failed for URL: {base_url}") from exc
