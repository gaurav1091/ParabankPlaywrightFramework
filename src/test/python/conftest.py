import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_MAIN_PYTHON = PROJECT_ROOT / "src" / "main" / "python"
SRC_TEST_PYTHON = PROJECT_ROOT / "src" / "test" / "python"

for path in (SRC_MAIN_PYTHON, SRC_TEST_PYTHON):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

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
    "hooks.pytest_bdd_hooks",
    "stepdefinitions.ui.application_launch_steps",
    "stepdefinitions.ui.login_steps",
    "stepdefinitions.ui.accounts_overview_steps",
    "stepdefinitions.ui.open_new_account_steps",
    "stepdefinitions.ui.transfer_funds_steps",
    "stepdefinitions.ui.bill_pay_steps",
    "stepdefinitions.ui.find_transactions_steps",
    "stepdefinitions.api.account_api_steps",
    "stepdefinitions.api.customer_api_steps",
    "stepdefinitions.hybrid.account_hybrid_steps",
    "stepdefinitions.hybrid.account_creation_hybrid_steps",
)

LOGGER = FrameworkLogger.get_logger("parabank_framework.conftest")
REPORTS_DIR = Path("test-output/reports")
REPORT_IMAGES_DIR = REPORTS_DIR / "images"

RETRY_STATS = {
    "rerun_events": 0,
    "per_test_reruns": {},
    "recovered_tests": set(),
    "still_failing_after_rerun": set(),
}

RETRY_RUNTIME_CONFIG = {
    "enabled": False,
    "configured_retry_enabled": False,
    "count": 0,
    "delay_seconds": 0,
}

PARALLEL_RUNTIME_CONFIG = {
    "enabled": False,
    "worker_count": 1,
    "dist_mode": "no",
    "parallel_mode": "off",
    "serial_marker_name": "serial",
    "include_serial_in_parallel": False,
    "worker_id": "master",
    "is_xdist_worker": False,
    "is_controller": True,
}


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--env", action="store", default=None, help="Execution environment: qa, stage, dev")
    parser.addoption("--framework-browser", action="store", default=None, help="Framework browser: chrome, firefox, edge")
    parser.addoption("--framework-headless", action="store", default=None, help="Framework headless mode: true/false")
    parser.addoption("--execution-mode", action="store", default=None, help="Execution mode: local/remote")
    parser.addoption("--remote-provider", action="store", default=None, help="Remote provider: browserstack")
    parser.addoption("--parallel-enabled", action="store", default=None, help="Enable/disable framework-driven parallel mode: true/false")
    parser.addoption("--thread-count", action="store", default=None, help="Parallel worker count equivalent")
    parser.addoption("--data-provider-thread-count", action="store", default=None, help="Parity placeholder with Java framework")
    parser.addoption("--dist-mode", action="store", default=None, help="xdist distribution mode: load, loadscope, loadfile, worksteal, no")
    parser.addoption("--include-serial-in-parallel", action="store_true", default=False, help="Allow tests marked serial to remain in a parallel session")
    parser.addoption("--retry-count", action="store", default=None, help="Retry count")
    parser.addoption("--retry-delay", action="store", default=None, help="Retry delay in seconds")
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
        "parallel.enabled": pytestconfig.getoption("--parallel-enabled"),
        "thread.count": pytestconfig.getoption("--thread-count"),
        "data.provider.thread.count": pytestconfig.getoption("--data-provider-thread-count"),
        "parallel.dist.mode": pytestconfig.getoption("--dist-mode"),
        "retry.count": pytestconfig.getoption("--retry-count"),
        "retry.delay.seconds": pytestconfig.getoption("--retry-delay"),
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


def _get_worker_id(config: pytest.Config | None = None) -> str:
    if config is not None and hasattr(config, "workerinput"):
        worker_id = config.workerinput.get("workerid")
        if worker_id:
            return str(worker_id)

    env_worker_id = os.getenv("PYTEST_XDIST_WORKER")
    if env_worker_id:
        return env_worker_id.strip()

    return "master"


def _is_xdist_worker(config: pytest.Config) -> bool:
    return hasattr(config, "workerinput")


def _is_controller_process(config: pytest.Config) -> bool:
    return not _is_xdist_worker(config)


def _get_numprocesses(config: pytest.Config) -> int:
    numprocesses = getattr(config.option, "numprocesses", None)

    if numprocesses in (None, "auto", "logical"):
        return 0

    try:
        return int(numprocesses)
    except (TypeError, ValueError):
        return 0


def _is_parallel_session(config: pytest.Config) -> bool:
    if _is_xdist_worker(config):
        return True

    return _get_numprocesses(config) > 1


def _build_trace_file_path(request: pytest.FixtureRequest) -> str:
    worker_id = _get_worker_id(request.config)
    file_name = f"{worker_id}_{_safe_node_name(request.node.nodeid)}.zip"
    return str(Path(FrameworkConstants.TRACES_FOLDER) / file_name)


def _build_report_image_path(nodeid: str, when: str, worker_id: str) -> Path:
    safe_name = f"failure_{worker_id}_{_safe_node_name(nodeid)}_{when}.png"
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


def _initialize_retry_stats() -> None:
    RETRY_STATS["rerun_events"] = 0
    RETRY_STATS["per_test_reruns"] = {}
    RETRY_STATS["recovered_tests"] = set()
    RETRY_STATS["still_failing_after_rerun"] = set()


def _get_retry_stats() -> dict:
    return RETRY_STATS


def _resolve_retry_runtime_config(config_manager: ConfigManager) -> dict[str, int | bool]:
    retry_enabled = config_manager.is_retry_enabled()
    retry_count = max(0, config_manager.get_retry_count()) if retry_enabled else 0
    retry_delay_seconds = max(0, config_manager.get_retry_delay_seconds())

    return {
        "enabled": retry_enabled and retry_count > 0,
        "configured_retry_enabled": retry_enabled,
        "count": retry_count,
        "delay_seconds": retry_delay_seconds,
    }


def _apply_retry_runtime_config(config: pytest.Config, config_manager: ConfigManager) -> dict[str, int | bool]:
    retry_runtime_config = _resolve_retry_runtime_config(config_manager)

    config.option.reruns = retry_runtime_config["count"]
    config.option.reruns_delay = retry_runtime_config["delay_seconds"]

    RETRY_RUNTIME_CONFIG.update(retry_runtime_config)
    return retry_runtime_config


def _get_retry_runtime_config() -> dict[str, int | bool]:
    return RETRY_RUNTIME_CONFIG


def _resolve_parallel_runtime_config(
    config: pytest.Config,
    config_manager: ConfigManager,
) -> dict[str, int | bool | str]:
    worker_count = max(1, config_manager.get_thread_count())
    detected_numprocesses = _get_numprocesses(config)

    if detected_numprocesses > 1:
        worker_count = detected_numprocesses

    is_parallel_active = _is_parallel_session(config)
    dist_mode = getattr(config.option, "dist", None) or config_manager.get_parallel_dist_mode()
    include_serial_in_parallel = config.getoption("--include-serial-in-parallel")
    serial_marker_name = config_manager.get_serial_marker_name()

    return {
        "enabled": is_parallel_active,
        "worker_count": worker_count,
        "dist_mode": str(dist_mode or "no"),
        "parallel_mode": config_manager.get_parallel_mode(),
        "serial_marker_name": serial_marker_name,
        "include_serial_in_parallel": include_serial_in_parallel,
        "worker_id": _get_worker_id(config),
        "is_xdist_worker": _is_xdist_worker(config),
        "is_controller": _is_controller_process(config),
    }


def _apply_parallel_runtime_config(
    config: pytest.Config,
    config_manager: ConfigManager,
) -> dict[str, int | bool | str]:
    parallel_runtime_config = _resolve_parallel_runtime_config(config, config_manager)
    PARALLEL_RUNTIME_CONFIG.update(parallel_runtime_config)
    return parallel_runtime_config


def _get_parallel_runtime_config() -> dict[str, int | bool | str]:
    return PARALLEL_RUNTIME_CONFIG


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    suite = config.getoption("--suite")
    run_manual = config.getoption("--run-manual")
    run_quarantined = config.getoption("--run-quarantined")
    parallel_runtime_config = _get_parallel_runtime_config()
    serial_marker_name = str(parallel_runtime_config["serial_marker_name"])
    include_serial_in_parallel = bool(parallel_runtime_config["include_serial_in_parallel"])
    parallel_active = bool(parallel_runtime_config["enabled"])

    selected_items: list[pytest.Item] = []
    deselected_items: list[pytest.Item] = []

    for item in items:
        if not run_manual and _has_marker(item, "manual"):
            deselected_items.append(item)
            continue

        if not run_quarantined and _has_marker(item, "quarantined"):
            deselected_items.append(item)
            continue

        if parallel_active and not include_serial_in_parallel and _has_marker(item, serial_marker_name):
            deselected_items.append(item)
            continue

        if not _matches_suite(item, suite):
            deselected_items.append(item)
            continue

        selected_items.append(item)

    if deselected_items and _is_controller_process(config):
        config.hook.pytest_deselected(items=deselected_items)

    items[:] = selected_items


def pytest_report_header(config: pytest.Config) -> str:
    suite = config.getoption("--suite")
    run_manual = config.getoption("--run-manual")
    run_quarantined = config.getoption("--run-quarantined")
    execution_mode = config.getoption("--execution-mode") or "configured-default"
    browser = config.getoption("--framework-browser") or "configured-default"
    retry_runtime_config = _get_retry_runtime_config()
    parallel_runtime_config = _get_parallel_runtime_config()

    return (
        f"Suite selection: {suite} | "
        f"Include manual: {run_manual} | "
        f"Include quarantined: {run_quarantined} | "
        f"Execution mode: {execution_mode} | "
        f"Browser: {browser} | "
        f"Retry enabled: {retry_runtime_config['enabled']} | "
        f"Retry count: {retry_runtime_config['count']} | "
        f"Retry delay(s): {retry_runtime_config['delay_seconds']} | "
        f"Parallel active: {parallel_runtime_config['enabled']} | "
        f"Worker count: {parallel_runtime_config['worker_count']} | "
        f"Dist mode: {parallel_runtime_config['dist_mode']} | "
        f"Serial marker: {parallel_runtime_config['serial_marker_name']}"
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


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return

    stats = _get_retry_stats()
    per_test_reruns = stats["per_test_reruns"]

    if report.outcome == "rerun":
        current_reruns = per_test_reruns.get(report.nodeid, 0) + 1
        per_test_reruns[report.nodeid] = current_reruns
        stats["rerun_events"] += 1

        LOGGER.warning(
            "RERUN scheduled | Worker=%s | Node=%s | Phase=%s | Attempt=%s",
            _get_worker_id(),
            report.nodeid,
            report.when,
            current_reruns,
        )
        return

    rerun_attempts = per_test_reruns.get(report.nodeid, 0)
    if rerun_attempts == 0:
        return

    if report.outcome == "passed":
        stats["recovered_tests"].add(report.nodeid)
        LOGGER.info(
            "RECOVERED after rerun | Worker=%s | Node=%s | Attempts=%s",
            _get_worker_id(),
            report.nodeid,
            rerun_attempts,
        )
    elif report.outcome == "failed":
        stats["still_failing_after_rerun"].add(report.nodeid)
        LOGGER.error(
            "FAILED after reruns exhausted | Worker=%s | Node=%s | Attempts=%s",
            _get_worker_id(),
            report.nodeid,
            rerun_attempts,
        )


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


def _create_artifact_directories() -> None:
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.REPORTS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.SCREENSHOTS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.CUCUMBER_REPORTS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.LOGS_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.TRACES_FOLDER)
    ReportPathManager.create_directory_if_not_exists(FrameworkConstants.VIDEOS_FOLDER)
    ReportPathManager.create_directory_if_not_exists("test-output/allure-results")
    ReportPathManager.create_directory_if_not_exists(str(REPORT_IMAGES_DIR))


def pytest_configure(config: pytest.Config) -> None:
    load_dotenv()
    FrameworkLogger.configure_logging()
    logger = FrameworkLogger.get_logger("parabank_framework.bootstrap")

    overrides = _build_overrides(config)
    config_manager = ConfigManager.initialize(overrides)

    _initialize_retry_stats()
    retry_runtime_config = _apply_retry_runtime_config(config, config_manager)
    parallel_runtime_config = _apply_parallel_runtime_config(config, config_manager)

    if parallel_runtime_config["is_controller"]:
        _cleanup_artifacts_if_enabled(config_manager)
    else:
        logger.info(
            "XDIST worker detected: %s. Skipping controller-only artifact cleanup.",
            parallel_runtime_config["worker_id"],
        )

    _create_artifact_directories()

    if parallel_runtime_config["is_controller"]:
        StartupValidator.validate_or_throw()
    else:
        logger.info(
            "XDIST worker detected: %s. Skipping full startup validation because controller already handled it.",
            parallel_runtime_config["worker_id"],
        )

    logger.info("Framework bootstrapped successfully.")
    logger.info("Worker ID         : %s", parallel_runtime_config["worker_id"])
    logger.info("Is Controller     : %s", parallel_runtime_config["is_controller"])
    logger.info("Is XDIST Worker   : %s", parallel_runtime_config["is_xdist_worker"])
    logger.info("Environment       : %s", config_manager.get_current_environment())
    logger.info("Browser           : %s", config_manager.get_browser())
    logger.info("Headless          : %s", config_manager.is_headless())
    logger.info("Execution Mode    : %s", config_manager.get_execution_mode())
    logger.info("Remote Provider   : %s", config_manager.get_remote_provider())
    logger.info("Base URL          : %s", config_manager.get_base_url())
    logger.info("API Base URL      : %s", config_manager.get_api_base_url())
    logger.info("Parallel Enabled  : %s", parallel_runtime_config["enabled"])
    logger.info("Parallel Mode     : %s", parallel_runtime_config["parallel_mode"])
    logger.info("Dist Mode         : %s", parallel_runtime_config["dist_mode"])
    logger.info("Thread Count      : %s", parallel_runtime_config["worker_count"])
    logger.info("DP Thread Count   : %s", config_manager.get_data_provider_thread_count())
    logger.info("Serial Marker     : %s", parallel_runtime_config["serial_marker_name"])
    logger.info("Include Serial    : %s", parallel_runtime_config["include_serial_in_parallel"])
    logger.info("Retry Config On   : %s", retry_runtime_config["configured_retry_enabled"])
    logger.info("Retry Active      : %s", retry_runtime_config["enabled"])
    logger.info("Retry Count       : %s", retry_runtime_config["count"])
    logger.info("Retry Delay (s)   : %s", retry_runtime_config["delay_seconds"])
    logger.info("Selected Suite    : %s", config.getoption("--suite"))
    logger.info("Flaky Policy      : quarantined tests are excluded unless --run-quarantined is used")
    logger.info(
        "Parallel Policy   : tests marked '%s' are excluded from parallel runs unless --include-serial-in-parallel is used",
        parallel_runtime_config["serial_marker_name"],
    )

    browserstack_project = config_manager.get_property("browserstack.project.name")
    browserstack_build = config_manager.get_property("browserstack.build.name")
    browserstack_session = config_manager.get_property("browserstack.session.name")

    if browserstack_project:
        logger.info("BS Project        : %s", browserstack_project)
    if browserstack_build:
        logger.info("BS Build          : %s", browserstack_build)
    if browserstack_session:
        logger.info("BS Session        : %s", browserstack_session)


@pytest.fixture(scope="session")
def framework_config() -> ConfigManager:
    return ConfigManager.instance()


@pytest.fixture(scope="session")
def framework_playwright(framework_config: ConfigManager) -> Playwright:
    logger = FrameworkLogger.get_logger("parabank_framework.playwright")
    logger.info("Starting Playwright engine. Worker=%s", _get_worker_id())

    playwright = sync_playwright().start()
    DriverManager.set_playwright(playwright)

    yield playwright

    logger.info("Stopping Playwright engine. Worker=%s", _get_worker_id())
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
    logger.info("Initializing browser for session. Worker=%s", _get_worker_id())

    browser = BrowserFactory.launch_browser(framework_playwright, framework_config)
    DriverManager.set_browser(browser)

    yield browser

    logger.info("Closing browser for session. Worker=%s", _get_worker_id())
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

    logger.info(
        "Creating browser context for test: %s | Worker=%s",
        request.node.nodeid,
        _get_worker_id(request.config),
    )
    context = framework_browser.new_context(**context_options)
    DriverManager.set_context(context)

    context.set_default_timeout(framework_config.get_playwright_action_timeout_millis())
    context.set_default_navigation_timeout(framework_config.get_playwright_navigation_timeout_millis())

    trace_path = _build_trace_file_path(request)

    if framework_config.is_playwright_trace_enabled():
        logger.info(
            "Starting tracing for test: %s | Worker=%s",
            request.node.nodeid,
            _get_worker_id(request.config),
        )
        context.tracing.start(
            screenshots=framework_config.is_playwright_trace_screenshots_enabled(),
            snapshots=framework_config.is_playwright_trace_snapshots_enabled(),
            sources=framework_config.is_playwright_trace_sources_enabled(),
        )

    yield context

    try:
        if framework_config.is_playwright_trace_enabled():
            logger.info(
                "Stopping tracing and saving trace: %s | Worker=%s",
                trace_path,
                _get_worker_id(request.config),
            )
            context.tracing.stop(path=trace_path)

            if _was_test_unsuccessful(request):
                try:
                    _attach_trace_to_allure(trace_path)
                    logger.info(
                        "Attached trace to Allure for failed test: %s | Worker=%s",
                        request.node.nodeid,
                        _get_worker_id(request.config),
                    )
                except Exception as exc:
                    logger.warning(
                        "Failed attaching trace to Allure. Worker=%s | Node=%s | Error=%s",
                        _get_worker_id(request.config),
                        request.node.nodeid,
                        exc,
                    )
    finally:
        logger.info(
            "Closing browser context for test: %s | Worker=%s",
            request.node.nodeid,
            _get_worker_id(request.config),
        )
        context.close()
        DriverManager.clear_context()


@pytest.fixture(scope="function")
def framework_page(
    request: pytest.FixtureRequest,
    framework_context: BrowserContext,
    framework_config: ConfigManager,
) -> Page:
    logger = FrameworkLogger.get_logger("parabank_framework.page")
    worker_id = _get_worker_id(request.config)

    logger.info("Creating page for test: %s | Worker=%s", request.node.nodeid, worker_id)

    page = framework_context.new_page()
    page.set_default_timeout(framework_config.get_playwright_action_timeout_millis())
    page.set_default_navigation_timeout(framework_config.get_playwright_navigation_timeout_millis())
    DriverManager.set_page(page)

    yield page

    if _was_test_unsuccessful(request):
        try:
            REPORT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
            screenshot_path = _build_report_image_path(request.node.nodeid, "call", worker_id)
            page.screenshot(path=str(screenshot_path), full_page=True)
            request.node.failure_screenshot_path = str(screenshot_path)

            LOGGER.info(
                "Failure screenshot captured in framework_page fixture teardown. Worker=%s | Node=%s | Screenshot=%s",
                worker_id,
                request.node.nodeid,
                screenshot_path,
            )

            try:
                _attach_screenshot_to_allure(str(screenshot_path))
                _attach_text_to_allure("failure_url", page.url)
                _attach_text_to_allure("failure_title", page.title())
            except Exception as exc:
                LOGGER.warning(
                    "Failed attaching screenshot to Allure from framework_page teardown. Worker=%s | Node=%s | Error=%s",
                    worker_id,
                    request.node.nodeid,
                    exc,
                )
        except Exception as exc:
            LOGGER.warning(
                "Failed capturing screenshot in framework_page teardown. Worker=%s | Node=%s | Error=%s",
                worker_id,
                request.node.nodeid,
                exc,
            )

    logger.info("Closing page for test: %s | Worker=%s", request.node.nodeid, worker_id)
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


def pytest_terminal_summary(terminalreporter, exitstatus: int, config: pytest.Config) -> None:
    retry_runtime_config = _get_retry_runtime_config()
    parallel_runtime_config = _get_parallel_runtime_config()
    stats = _get_retry_stats()
    rerun_events = stats["rerun_events"]
    recovered_tests = sorted(stats["recovered_tests"])
    still_failing_after_rerun = sorted(stats["still_failing_after_rerun"])

    terminalreporter.section("Framework Parallel Summary", sep="=")
    terminalreporter.write_line(f"Parallel active         : {parallel_runtime_config['enabled']}")
    terminalreporter.write_line(f"Parallel mode           : {parallel_runtime_config['parallel_mode']}")
    terminalreporter.write_line(f"Worker count            : {parallel_runtime_config['worker_count']}")
    terminalreporter.write_line(f"Dist mode               : {parallel_runtime_config['dist_mode']}")
    terminalreporter.write_line(f"Serial marker           : {parallel_runtime_config['serial_marker_name']}")
    terminalreporter.write_line(
        f"Include serial in parallel: {parallel_runtime_config['include_serial_in_parallel']}"
    )

    terminalreporter.section("Framework Retry Summary", sep="=")
    terminalreporter.write_line(f"Retry configured        : {retry_runtime_config['configured_retry_enabled']}")
    terminalreporter.write_line(f"Retry active            : {retry_runtime_config['enabled']}")
    terminalreporter.write_line(f"Retry count             : {retry_runtime_config['count']}")
    terminalreporter.write_line(f"Retry delay (s)         : {retry_runtime_config['delay_seconds']}")
    terminalreporter.write_line(f"Total rerun events      : {rerun_events}")
    terminalreporter.write_line(f"Recovered after rerun   : {len(recovered_tests)}")
    terminalreporter.write_line(f"Failed after rerun      : {len(still_failing_after_rerun)}")

    if recovered_tests:
        terminalreporter.write_line("Recovered tests:")
        for nodeid in recovered_tests:
            terminalreporter.write_line(f"  - {nodeid}")

    if still_failing_after_rerun:
        terminalreporter.write_line("Still failing after retries:")
        for nodeid in still_failing_after_rerun:
            terminalreporter.write_line(f"  - {nodeid}")