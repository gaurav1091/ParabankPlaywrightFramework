import pytest
from dotenv import load_dotenv

from com.parabank.automation.config.config_manager import ConfigManager
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


def pytest_configure(config: pytest.Config) -> None:
    load_dotenv()
    FrameworkLogger.configure_logging()
    logger = FrameworkLogger.get_logger("parabank_framework.bootstrap")

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