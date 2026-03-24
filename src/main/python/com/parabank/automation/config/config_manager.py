from __future__ import annotations

from urllib.parse import quote, urlparse

from com.parabank.automation.config.environment_manager import EnvironmentManager
from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.config.property_reader import PropertyReader
from com.parabank.automation.config.sensitive_data_resolver import SensitiveDataResolver


class ConfigManager:
    _instance: ConfigManager | None = None
    _overrides: dict[str, str] = {}

    def __init__(self) -> None:
        framework_config_path = (
            f"{FrameworkConstants.CONFIG_RESOURCES_ROOT}/{FrameworkConstants.FRAMEWORK_CONFIG_FILE}"
        )
        environment_config_path = (
            f"{FrameworkConstants.CONFIG_RESOURCES_ROOT}/"
            f"{EnvironmentManager.get_environment_config_file_name(self._overrides.get('env'))}"
        )

        self.framework_properties = PropertyReader.load_properties(framework_config_path)
        self.environment_properties = PropertyReader.load_properties(environment_config_path)

    @classmethod
    def initialize(cls, overrides: dict[str, str] | None = None) -> "ConfigManager":
        cls._overrides = cls._sanitize_overrides(overrides or {})
        cls._instance = ConfigManager()
        return cls._instance

    @classmethod
    def instance(cls) -> "ConfigManager":
        if cls._instance is None:
            cls.initialize({})
        return cls._instance

    @staticmethod
    def _sanitize_overrides(overrides: dict[str, str]) -> dict[str, str]:
        sanitized: dict[str, str] = {}

        for key, value in overrides.items():
            if value is None:
                continue

            text = str(value).strip()
            if text == "":
                continue

            sanitized[key] = text

        return sanitized

    def get_property(self, key: str) -> str | None:
        if key in self._overrides:
            return self._overrides[key].strip()

        environment_value = self.environment_properties.get(key)
        if environment_value and environment_value.strip():
            return environment_value.strip()

        framework_value = self.framework_properties.get(key)
        if framework_value and framework_value.strip():
            return framework_value.strip()

        return None

    def get_browser(self) -> str:
        return (self.get_property("browser") or FrameworkConstants.CHROME).strip().lower()

    def get_playwright_browser_name(self) -> str:
        browser = self.get_browser()
        return FrameworkConstants.PLAYWRIGHT_BROWSER_NAME_MAP.get(browser, "chromium")

    def get_playwright_browser_channel(self) -> str | None:
        browser = self.get_browser()
        channel = FrameworkConstants.PLAYWRIGHT_BROWSER_CHANNEL_MAP.get(browser, "")
        return channel if channel else None

    def is_headless(self) -> bool:
        return self._to_bool(self.get_property("headless"), default=False)

    def get_base_url(self) -> str:
        return self.get_property("base.url") or ""

    def get_api_base_url(self) -> str:
        return self.get_property("api.base.url") or ""

    def get_username(self) -> str:
        return SensitiveDataResolver.resolve_credential_value(
            self.get_property("username"),
            "Config username property",
        )

    def get_password(self) -> str:
        return SensitiveDataResolver.resolve_credential_value(
            self.get_property("password"),
            "Config password property",
        )

    def get_execution_mode(self) -> str:
        return (
            self.get_property("execution.mode")
            or FrameworkConstants.EXECUTION_MODE_LOCAL
        ).strip().lower()

    def is_remote_execution(self) -> bool:
        return self.get_execution_mode() == FrameworkConstants.EXECUTION_MODE_REMOTE

    def get_remote_provider(self) -> str:
        return (
            self.get_property("remote.provider")
            or FrameworkConstants.REMOTE_PROVIDER_SELENIUM_GRID
        ).strip().lower()

    def is_selenium_grid_execution(self) -> bool:
        return self.is_remote_execution() and (
            self.get_remote_provider() == FrameworkConstants.REMOTE_PROVIDER_SELENIUM_GRID
        )

    def is_browserstack_execution(self) -> bool:
        return self.is_remote_execution() and (
            self.get_remote_provider() == FrameworkConstants.REMOTE_PROVIDER_BROWSERSTACK
        )

    def get_selenium_remote_url(self) -> str:
        return (
            self.get_property("selenium.remote.url")
            or FrameworkConstants.DEFAULT_SELENIUM_REMOTE_URL
        ).strip()

    def get_browserstack_hub_url(self) -> str:
        return (
            self.get_property("browserstack.hub.url")
            or FrameworkConstants.DEFAULT_BROWSERSTACK_HUB_URL
        ).strip()

    def get_browserstack_username(self) -> str:
        return SensitiveDataResolver.resolve_credential_value(
            self.get_property("browserstack.username"),
            "BrowserStack username",
        )

    def get_browserstack_access_key(self) -> str:
        return SensitiveDataResolver.resolve_credential_value(
            self.get_property("browserstack.access.key"),
            "BrowserStack access key",
        )

    def get_browserstack_remote_url(self) -> str:
        hub_url = self.get_browserstack_hub_url()
        parsed = urlparse(hub_url)

        encoded_username = quote(self.get_browserstack_username(), safe="")
        encoded_access_key = quote(self.get_browserstack_access_key(), safe="")

        host = parsed.hostname or ""
        port = f":{parsed.port}" if parsed.port else ""
        auth_netloc = f"{encoded_username}:{encoded_access_key}@{host}{port}"

        return parsed._replace(netloc=auth_netloc).geturl()

    def get_browserstack_os(self) -> str:
        return (
            self.get_property("browserstack.os")
            or FrameworkConstants.DEFAULT_BROWSERSTACK_OS
        ).strip()

    def get_browserstack_os_version(self) -> str:
        return (
            self.get_property("browserstack.os.version")
            or FrameworkConstants.DEFAULT_BROWSERSTACK_OS_VERSION
        ).strip()

    def get_browserstack_browser_version(self) -> str:
        return (
            self.get_property("browserstack.browser.version")
            or FrameworkConstants.DEFAULT_BROWSERSTACK_BROWSER_VERSION
        ).strip()

    def get_browserstack_project_name(self) -> str:
        return (
            self.get_property("browserstack.project.name")
            or FrameworkConstants.DEFAULT_BROWSERSTACK_PROJECT_NAME
        ).strip()

    def get_browserstack_build_name(self) -> str:
        return (
            self.get_property("browserstack.build.name")
            or FrameworkConstants.DEFAULT_BROWSERSTACK_BUILD_NAME
        ).strip()

    def get_browserstack_session_name(self) -> str:
        return (
            self.get_property("browserstack.session.name")
            or FrameworkConstants.DEFAULT_BROWSERSTACK_SESSION_NAME
        ).strip()

    def is_browserstack_local_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("browserstack.local"),
            default=FrameworkConstants.DEFAULT_BROWSERSTACK_LOCAL,
        )

    def is_browserstack_debug_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("browserstack.debug"),
            default=FrameworkConstants.DEFAULT_BROWSERSTACK_DEBUG,
        )

    def is_browserstack_network_logs_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("browserstack.network.logs"),
            default=FrameworkConstants.DEFAULT_BROWSERSTACK_NETWORK_LOGS,
        )

    def get_browserstack_console_logs(self) -> str:
        return (
            self.get_property("browserstack.console.logs")
            or FrameworkConstants.DEFAULT_BROWSERSTACK_CONSOLE_LOGS
        ).strip()

    def get_implicit_wait(self) -> int:
        return self._get_int_property("implicit.wait", FrameworkConstants.DEFAULT_IMPLICIT_WAIT)

    def get_explicit_wait(self) -> int:
        return self._get_int_property("explicit.wait", FrameworkConstants.DEFAULT_EXPLICIT_WAIT)

    def get_page_load_timeout(self) -> int:
        return self._get_int_property("page.load.timeout", FrameworkConstants.DEFAULT_PAGE_LOAD_TIMEOUT)

    def get_script_timeout(self) -> int:
        return self._get_int_property("script.timeout", FrameworkConstants.DEFAULT_SCRIPT_TIMEOUT)

    def is_highlight_elements_enabled(self) -> bool:
        return self._to_bool(self.get_property("highlight.elements"), default=False)

    def is_screenshot_on_pass_enabled(self) -> bool:
        return self._to_bool(self.get_property("take.screenshot.on.pass"), default=False)

    def is_screenshot_on_fail_enabled(self) -> bool:
        return self._to_bool(self.get_property("take.screenshot.on.fail"), default=True)

    def get_thread_count(self) -> int:
        return self._get_int_property("thread.count", 3)

    def get_data_provider_thread_count(self) -> int:
        return self._get_int_property("data.provider.thread.count", 3)

    def get_parallel_mode(self) -> str:
        return (self.get_property("parallel.mode") or "methods").strip().lower()

    def is_retry_enabled(self) -> bool:
        return self._to_bool(self.get_property("retry.enabled"), default=True)

    def get_retry_count(self) -> int:
        return self._get_int_property("retry.count", 1)

    def get_smart_wait_polling_millis(self) -> int:
        return self._get_int_property(
            "smart.wait.polling.millis",
            FrameworkConstants.DEFAULT_SMART_WAIT_POLLING_MILLIS,
        )

    def get_resilient_find_retries(self) -> int:
        return self._get_int_property(
            "resilient.find.retries",
            FrameworkConstants.DEFAULT_RESILIENT_FIND_RETRIES,
        )

    def get_resilient_find_delay_millis(self) -> int:
        return self._get_int_property(
            "resilient.find.delay.millis",
            FrameworkConstants.DEFAULT_RESILIENT_FIND_DELAY_MILLIS,
        )

    def get_api_connect_timeout_seconds(self) -> int:
        return self._get_int_property(
            "api.connect.timeout.seconds",
            FrameworkConstants.DEFAULT_API_CONNECT_TIMEOUT_SECONDS,
        )

    def get_api_read_timeout_seconds(self) -> int:
        return self._get_int_property(
            "api.read.timeout.seconds",
            FrameworkConstants.DEFAULT_API_READ_TIMEOUT_SECONDS,
        )

    def is_startup_validation_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("startup.validation.enabled"),
            default=FrameworkConstants.DEFAULT_STARTUP_VALIDATION_ENABLED,
        )

    def get_startup_validation_timeout_seconds(self) -> int:
        return self._get_int_property(
            "startup.validation.timeout.seconds",
            FrameworkConstants.DEFAULT_STARTUP_VALIDATION_TIMEOUT_SECONDS,
        )

    def get_playwright_slow_mo_millis(self) -> int:
        return self._get_int_property(
            "playwright.slow.mo.millis",
            FrameworkConstants.DEFAULT_PLAYWRIGHT_SLOW_MO_MILLIS,
        )

    def get_playwright_browser_launch_timeout_millis(self) -> int:
        return self._get_int_property(
            "playwright.browser.launch.timeout.millis",
            FrameworkConstants.DEFAULT_PLAYWRIGHT_BROWSER_LAUNCH_TIMEOUT_MILLIS,
        )

    def get_playwright_action_timeout_millis(self) -> int:
        return self._get_int_property(
            "playwright.action.timeout.millis",
            FrameworkConstants.DEFAULT_PLAYWRIGHT_ACTION_TIMEOUT_MILLIS,
        )

    def get_playwright_navigation_timeout_millis(self) -> int:
        return self._get_int_property(
            "playwright.navigation.timeout.millis",
            FrameworkConstants.DEFAULT_PLAYWRIGHT_NAVIGATION_TIMEOUT_MILLIS,
        )

    def is_playwright_trace_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("playwright.trace.enabled"),
            default=FrameworkConstants.DEFAULT_PLAYWRIGHT_TRACE_ENABLED,
        )

    def is_playwright_trace_screenshots_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("playwright.trace.screenshots"),
            default=FrameworkConstants.DEFAULT_PLAYWRIGHT_TRACE_SCREENSHOTS,
        )

    def is_playwright_trace_snapshots_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("playwright.trace.snapshots"),
            default=FrameworkConstants.DEFAULT_PLAYWRIGHT_TRACE_SNAPSHOTS,
        )

    def is_playwright_trace_sources_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("playwright.trace.sources"),
            default=FrameworkConstants.DEFAULT_PLAYWRIGHT_TRACE_SOURCES,
        )

    def is_playwright_video_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("playwright.video.enabled"),
            default=FrameworkConstants.DEFAULT_PLAYWRIGHT_VIDEO_ENABLED,
        )

    def get_playwright_video_width(self) -> int:
        return self._get_int_property(
            "playwright.video.width",
            FrameworkConstants.DEFAULT_PLAYWRIGHT_VIDEO_WIDTH,
        )

    def get_playwright_video_height(self) -> int:
        return self._get_int_property(
            "playwright.video.height",
            FrameworkConstants.DEFAULT_PLAYWRIGHT_VIDEO_HEIGHT,
        )

    def get_playwright_viewport_width(self) -> int:
        return self._get_int_property(
            "playwright.viewport.width",
            FrameworkConstants.DEFAULT_PLAYWRIGHT_VIEWPORT_WIDTH,
        )

    def get_playwright_viewport_height(self) -> int:
        return self._get_int_property(
            "playwright.viewport.height",
            FrameworkConstants.DEFAULT_PLAYWRIGHT_VIEWPORT_HEIGHT,
        )

    def is_playwright_accept_downloads_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("playwright.accept.downloads"),
            default=FrameworkConstants.DEFAULT_PLAYWRIGHT_ACCEPT_DOWNLOADS,
        )

    def is_playwright_ignore_https_errors_enabled(self) -> bool:
        return self._to_bool(
            self.get_property("playwright.ignore.https.errors"),
            default=FrameworkConstants.DEFAULT_PLAYWRIGHT_IGNORE_HTTPS_ERRORS,
        )

    def get_current_environment(self) -> str:
        return EnvironmentManager.get_current_environment(self._overrides.get("env"))

    @staticmethod
    def _to_bool(value: str | None, default: bool = False) -> bool:
        if value is None:
            return default
        return value.strip().lower() in {"true", "1", "yes", "y", "on"}

    def _get_int_property(self, key: str, default: int) -> int:
        value = self.get_property(key)

        if value is None or value.strip() == "":
            return default

        try:
            return int(value.strip())
        except ValueError as exc:
            raise ValueError(f"Invalid integer value for property '{key}': {value}") from exc