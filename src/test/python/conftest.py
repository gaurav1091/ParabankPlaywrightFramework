import re
from pathlib import Path

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.driver.browser_factory import BrowserFactory
from com.parabank.automation.driver.browser_options_factory import BrowserOptionsFactory
from com.parabank.automation.driver.driver_manager import DriverManager
from com.parabank.automation.reports.report_path_manager import ReportPathManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger
from com.parabank.automation.validation.startup_validator import StartupValidator


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--env", action="store", default=None, help="Execution environment: qa, stage, dev")
    parser.addoption(
        "--framework-browser",
        action="store",
        default=None,
        help="Framework browser: chrome, firefox, edge",
    )
    parser.addoption(
        "--framework-headless",
        action="store",
        default=None,
        help="Framework headless mode: true/false",
    )
    parser.addoption(
        "--execution-mode",
        action="store",
        default=None,
        help="Execution mode: local/remote",
    )
    parser.addoption(
        "--remote-provider",
        action="store",
        default=None,
        help="Remote provider: selenium-grid/browserstack",
    )
    parser.addoption(
        "--thread-count",
        action="store",
        default=None,
        help="Parallel worker count equivalent",
    )
    parser.addoption(
        "--data-provider-thread-count",
        action="store",
        default=None,
        help="Parity placeholder with Java framework",
    )
    parser.addoption("--retry-count", action="store", default=None, help="Retry count")
    parser.addoption(
        "--framework-base-url",
        action="store",
        default=None,
        help="Override application base url",
    )
    parser.addoption("--api-base-url", action="store", default=None, help="Override API base url")
    parser.addoption("--username", action="store", default=None, help="Override application username")
    parser.addoption("--password", action="store", default=None, help="Override application password")
    parser.addoption(
        "--startup-validation",
        action="store",
        default=None,
        help="Enable/disable startup validation true/false",
    )


def _build_overrides(pytestconfig: pytest.Config) -> dict[str, str]:
    mapping = {
        "env": pytestconfig.getoption("--env"),
        "browser": pytestconfig.getoption("--framework-browser"),
        "headless": pytestconfig.getoption("--framework-headless"),
        "execution.mode": pytestconfig.getoption("--execution-mode"),
        "remote.provider": pytestconfig.getoption("--remote-provider"),
        "thread.count": pytestconfig.getoption("--thread-count"),
        "data.provider.thread.count": pytestconfig.getoption("--data-provider-thread-count"),
        "retry.count": pytestconfig.getoption("--retry-count"),
        "base.url": pytestconfig.getoption("--framework-base-url"),
        "api.base.url": pytestconfig.getoption("--api-base-url"),
        "username": pytestconfig.getoption("--username"),
        "password": pytestconfig.getoption("--password"),
        "startup.validation.enabled": pytestconfig.getoption("--startup-validation"),
    }

    return {key: value for key, value in mapping.items() if value is not None}


def _safe_node_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", nodeid)


def _build_trace_file_path(request: pytest.FixtureRequest) -> str:
    file_name = f"{_safe_node_name(request.node.nodeid)}.zip"
    return str(Path(FrameworkConstants.TRACES_FOLDER) / file_name)


def pytest_configure(config: pytest.Config) -> None:
    load_dotenv()
    FrameworkLogger.configure_logging()
    logger = FrameworkLogger.get_logger("parabank_framework.bootstrap")

    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.REPORTS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.SCREENSHOTS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.CUCUMBER_REPORTS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.LOGS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.TRACES_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.VIDEOS_FOLDER)

    overrides = _build_overrides(config)
    config_manager = ConfigManager.initialize(overrides)

    StartupValidator.validate_or_throw()

    logger.info("Framework bootstrapped successfully.")
    logger.info("Environment      : %s", config_manager.get_current_environment())
    logger.info("Browser          : %s", config_manager.get_browser())
    logger.info("Headless         : %s", config_manager.is_headless())
    logger.info("Execution Mode   : %s", config_manager.get_execution_mode())
    logger.info("Remote Provider  : %s", config_manager.get_remote_provider())
    logger.info("Base URL         : %s", config_manager.get_base_url())
    logger.info("API Base URL     : %s", config_manager.get_api_base_url())
    logger.info("Thread Count     : %s", config_manager.get_thread_count())
    logger.info("DP Thread Count  : %s", config_manager.get_data_provider_thread_count())
    logger.info("Retry Enabled    : %s", config_manager.is_retry_enabled())
    logger.info("Retry Count      : %s", config_manager.get_retry_count())


@pytest.fixture(scope="session")
def framework_config() -> ConfigManager:
    return ConfigManager.instance()


@pytest.fixture(scope="session")
def framework_playwright(framework_config: ConfigManager) -> Playwright:
    logger = FrameworkLogger.get_logger("parabank_framework.playwright")
    logger.info("Starting Playwright engine.")

    playwright = sync_playwright().start()
    DriverManager.set_playwright(playwright)

    yield playwright

    logger.info("Stopping Playwright engine.")
    try:
        playwright.stop()
    finally:
        DriverManager.clear_playwright()


@pytest.fixture(scope="session")
def framework_browser(
    framework_playwright: Playwright,
    framework_config: ConfigManager,
) -> Browser:
    logger = FrameworkLogger.get_logger("parabank_framework.browser")
    logger.info("Initializing browser for session.")

    browser = BrowserFactory.launch_browser(framework_playwright, framework_config)
    DriverManager.set_browser(browser)

    yield browser

    logger.info("Closing browser for session.")
    try:
        browser.close()
    finally:
        DriverManager.clear_browser()


@pytest.fixture(scope="function")
def framework_context(
    request: pytest.FixtureRequest,
    framework_browser: Browser,
    framework_config: ConfigManager,
) -> BrowserContext:
    logger = FrameworkLogger.get_logger("parabank_framework.context")
    context_options = BrowserOptionsFactory.build_context_options(framework_config)

    logger.info("Creating browser context for test: %s", request.node.nodeid)
    context = framework_browser.new_context(**context_options)
    DriverManager.set_context(context)

    context.set_default_timeout(framework_config.get_playwright_action_timeout_millis())
    context.set_default_navigation_timeout(framework_config.get_playwright_navigation_timeout_millis())

    if framework_config.is_playwright_trace_enabled():
        logger.info("Starting tracing for test: %s", request.node.nodeid)
        context.tracing.start(
            screenshots=framework_config.is_playwright_trace_screenshots_enabled(),
            snapshots=framework_config.is_playwright_trace_snapshots_enabled(),
            sources=framework_config.is_playwright_trace_sources_enabled(),
        )

    yield context

    try:
        if framework_config.is_playwright_trace_enabled():
            trace_path = _build_trace_file_path(request)
            logger.info("Stopping tracing and saving trace: %s", trace_path)
            context.tracing.stop(path=trace_path)
    finally:
        logger.info("Closing browser context for test: %s", request.node.nodeid)
        context.close()
        DriverManager.clear_context()


@pytest.fixture(scope="function")
def framework_page(
    request: pytest.FixtureRequest,
    framework_context: BrowserContext,
    framework_config: ConfigManager,
) -> Page:
    logger = FrameworkLogger.get_logger("parabank_framework.page")
    logger.info("Creating page for test: %s", request.node.nodeid)

    page = framework_context.new_page()
    page.set_default_timeout(framework_config.get_playwright_action_timeout_millis())
    page.set_default_navigation_timeout(framework_config.get_playwright_navigation_timeout_millis())
    DriverManager.set_page(page)

    yield page

    logger.info("Closing page for test: %s", request.node.nodeid)
    try:
        page.close()
    finally:
        DriverManager.clear_page()