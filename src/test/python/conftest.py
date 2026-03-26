import re
from pathlib import Path

import allure
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.driver.browser_factory import BrowserFactory
from com.parabank.automation.driver.browser_options_factory import BrowserOptionsFactory
from com.parabank.automation.driver.driver_manager import DriverManager
from com.parabank.automation.reports.report_path_manager import ReportPathManager
from com.parabank.automation.utils.artifact_cleanup_manager import ArtifactCleanupManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger
from com.parabank.automation.validation.startup_validator import StartupValidator


pytest_plugins = (
    "stepdefinitions.ui.login_accounts_overview_steps",
)

LOGGER = FrameworkLogger.get_logger("parabank_framework.conftest")
REPORTS_DIR = Path("test-output/reports")
REPORT_IMAGES_DIR = REPORTS_DIR / "images"


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--env", action="store", default=None, help="Execution environment: qa, stage, dev")
    parser.addoption("--framework-browser", action="store", default=None, help="Framework browser: chrome, firefox, edge")
    parser.addoption("--framework-headless", action="store", default=None, help="Framework headless mode: true/false")
    parser.addoption("--execution-mode", action="store", default=None, help="Execution mode: local/remote")
    parser.addoption("--remote-provider", action="store", default=None, help="Remote provider: browserstack")
    parser.addoption("--thread-count", action="store", default=None, help="Parallel worker count equivalent")
    parser.addoption("--data-provider-thread-count", action="store", default=None, help="Parity placeholder with Java framework")
    parser.addoption("--retry-count", action="store", default=None, help="Retry count")
    parser.addoption("--framework-base-url", action="store", default=None, help="Override application base url")
    parser.addoption("--api-base-url", action="store", default=None, help="Override API base url")
    parser.addoption("--username", action="store", default=None, help="Override application username")
    parser.addoption("--password", action="store", default=None, help="Override application password")
    parser.addoption("--startup-validation", action="store", default=None, help="Enable/disable startup validation true/false")

    parser.addoption(
        "--browserstack-project-name",
        action="store",
        default=None,
        help="Override BrowserStack project name",
    )
    parser.addoption(
        "--browserstack-build-name",
        action="store",
        default=None,
        help="Override BrowserStack build name",
    )
    parser.addoption(
        "--browserstack-session-name",
        action="store",
        default=None,
        help="Override BrowserStack session name",
    )

    parser.addoption(
        "--suite",
        action="store",
        default="all",
        choices=["all", "smoke", "regression", "sanity", "ui", "api", "hybrid"],
        help="Logical suite selection similar to Java runner classes.",
    )
    parser.addoption(
        "--run-manual",
        action="store_true",
        default=False,
        help="Include tests marked as manual.",
    )
    parser.addoption(
        "--run-quarantined",
        action="store_true",
        default=False,
        help="Include tests marked as quarantined.",
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
        "browserstack.project.name": pytestconfig.getoption("--browserstack-project-name"),
        "browserstack.build.name": pytestconfig.getoption("--browserstack-build-name"),
        "browserstack.session.name": pytestconfig.getoption("--browserstack-session-name"),
    }
    return {key: value for key, value in mapping.items() if value is not None}


def _safe_node_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", nodeid)


def _build_trace_file_path(request: pytest.FixtureRequest) -> str:
    file_name = f"{_safe_node_name(request.node.nodeid)}.zip"
    return str(Path(FrameworkConstants.TRACES_FOLDER) / file_name)


def _build_report_image_path(nodeid: str, when: str) -> Path:
    safe_name = f"failure_{_safe_node_name(nodeid)}_{when}.png"
    return REPORT_IMAGES_DIR / safe_name


def _was_test_unsuccessful(request: pytest.FixtureRequest) -> bool:
    rep_setup = getattr(request.node, "rep_setup", None)
    rep_call = getattr(request.node, "rep_call", None)
    return bool((rep_setup is not None and rep_setup.failed) or (rep_call is not None and rep_call.failed))


def _attach_trace_to_allure(trace_path: str) -> None:
    if Path(trace_path).exists():
        allure.attach.file(trace_path, name="playwright_trace", extension="zip")


def _attach_screenshot_to_allure(screenshot_path: str) -> None:
    path = Path(screenshot_path)
    if path.exists():
        allure.attach.file(
            str(path),
            name="failure_screenshot",
            attachment_type=allure.attachment_type.PNG,
        )


def _attach_text_to_allure(name: str, value: str) -> None:
    allure.attach(value, name=name, attachment_type=allure.attachment_type.TEXT)


def _has_marker(item: pytest.Item, marker_name: str) -> bool:
    return item.get_closest_marker(marker_name) is not None


def _matches_suite(item: pytest.Item, suite: str) -> bool:
    if suite == "all":
        return True

    if suite == "smoke":
        return _has_marker(item, "smoke")

    if suite == "regression":
        return _has_marker(item, "regression")

    if suite == "sanity":
        return _has_marker(item, "sanity")

    if suite == "ui":
        return _has_marker(item, "ui") and not _has_marker(item, "hybrid") and not _has_marker(item, "api")

    if suite == "api":
        return _has_marker(item, "api") and not _has_marker(item, "hybrid")

    if suite == "hybrid":
        return _has_marker(item, "hybrid")

    return True


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    suite = config.getoption("--suite")
    run_manual = config.getoption("--run-manual")
    run_quarantined = config.getoption("--run-quarantined")

    selected_items: list[pytest.Item] = []
    deselected_items: list[pytest.Item] = []

    for item in items:
        if not run_manual and _has_marker(item, "manual"):
            deselected_items.append(item)
            continue

        if not run_quarantined and _has_marker(item, "quarantined"):
            deselected_items.append(item)
            continue

        if not _matches_suite(item, suite):
            deselected_items.append(item)
            continue

        selected_items.append(item)

    if deselected_items:
        config.hook.pytest_deselected(items=deselected_items)

    items[:] = selected_items


def pytest_report_header(config: pytest.Config) -> str:
    suite = config.getoption("--suite")
    run_manual = config.getoption("--run-manual")
    run_quarantined = config.getoption("--run-quarantined")
    execution_mode = config.getoption("--execution-mode") or "configured-default"
    browser = config.getoption("--framework-browser") or "configured-default"

    return (
        f"Suite selection: {suite} | "
        f"Include manual: {run_manual} | "
        f"Include quarantined: {run_quarantined} | "
        f"Execution mode: {execution_mode} | "
        f"Browser: {browser}"
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()

    setattr(item, f"rep_{report.when}", report)

    if report.when != "teardown":
        return

    screenshot_path = getattr(item, "failure_screenshot_path", None)
    if not screenshot_path:
        return

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is None:
        return

    extras = getattr(report, "extras", [])
    relative_image_path = f"images/{Path(screenshot_path).name}"
    extras.append(pytest_html.extras.url(relative_image_path, name="failure_screenshot"))
    report.extras = extras


def _cleanup_artifacts_if_enabled(config_manager: ConfigManager) -> None:
    cleanup_enabled_raw = config_manager.get_property("artifact.cleanup.enabled")
    cleanup_enabled = str(cleanup_enabled_raw).strip().lower() in {"true", "1", "yes", "y", "on"}

    if not cleanup_enabled:
        LOGGER.info("Artifact cleanup is disabled.")
        return

    raw_directories = config_manager.get_property("artifact.cleanup.directories")
    directories_to_cleanup = ArtifactCleanupManager.parse_directories_property(raw_directories)

    if not directories_to_cleanup:
        LOGGER.info("No artifact directories configured for cleanup.")
        return

    LOGGER.info("Artifact cleanup enabled. Cleaning directories: %s", directories_to_cleanup)
    ArtifactCleanupManager.cleanup_directories(directories_to_cleanup)


def pytest_configure(config: pytest.Config) -> None:
    load_dotenv()
    FrameworkLogger.configure_logging()
    logger = FrameworkLogger.get_logger("parabank_framework.bootstrap")

    overrides = _build_overrides(config)
    config_manager = ConfigManager.initialize(overrides)

    _cleanup_artifacts_if_enabled(config_manager)

    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.REPORTS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.SCREENSHOTS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.CUCUMBER_REPORTS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.LOGS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.TRACES_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.VIDEOS_FOLDER)
    ReportPathManager.create_directory_if_not_exists("test-output/allure-results")

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
    logger.info("Selected Suite   : %s", config.getoption("--suite"))

    browserstack_project = config_manager.get_property("browserstack.project.name")
    browserstack_build = config_manager.get_property("browserstack.build.name")
    browserstack_session = config_manager.get_property("browserstack.session.name")

    if browserstack_project:
        logger.info("BS Project       : %s", browserstack_project)
    if browserstack_build:
        logger.info("BS Build         : %s", browserstack_build)
    if browserstack_session:
        logger.info("BS Session       : %s", browserstack_session)


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

    trace_path = _build_trace_file_path(request)

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
            logger.info("Stopping tracing and saving trace: %s", trace_path)
            context.tracing.stop(path=trace_path)

            if _was_test_unsuccessful(request):
                try:
                    _attach_trace_to_allure(trace_path)
                    logger.info("Attached trace to Allure for failed test: %s", request.node.nodeid)
                except Exception as exc:
                    logger.warning(
                        "Failed attaching trace to Allure. Node=%s | Error=%s",
                        request.node.nodeid,
                        exc,
                    )
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

    if _was_test_unsuccessful(request):
        try:
            REPORT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
            screenshot_path = _build_report_image_path(request.node.nodeid, "call")
            page.screenshot(path=str(screenshot_path), full_page=True)
            request.node.failure_screenshot_path = str(screenshot_path)

            LOGGER.info(
                "Failure screenshot captured in framework_page fixture teardown. Node=%s | Screenshot=%s",
                request.node.nodeid,
                screenshot_path,
            )

            try:
                _attach_screenshot_to_allure(str(screenshot_path))
                _attach_text_to_allure("failure_url", page.url)
                _attach_text_to_allure("failure_title", page.title())
            except Exception as exc:
                LOGGER.warning(
                    "Failed attaching screenshot to Allure from framework_page teardown. Node=%s | Error=%s",
                    request.node.nodeid,
                    exc,
                )
        except Exception as exc:
            LOGGER.warning(
                "Failed capturing screenshot in framework_page teardown. Node=%s | Error=%s",
                request.node.nodeid,
                exc,
            )

    logger.info("Closing page for test: %s", request.node.nodeid)
    try:
        page.close()
    finally:
        DriverManager.clear_page()


@pytest.fixture(scope="function")
def framework_context_object(
    framework_page: Page,
    framework_config: ConfigManager,
) -> FrameworkContext:
    return FrameworkContext(framework_page, framework_config)


@pytest.fixture(scope="function")
def test_context(framework_context_object: FrameworkContext) -> FrameworkContext:
    return framework_context_object