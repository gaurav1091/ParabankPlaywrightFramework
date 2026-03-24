from playwright.sync_api import Browser, Playwright

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.driver.browser_options_factory import BrowserOptionsFactory
from com.parabank.automation.exceptions.driver_initialization_exception import DriverInitializationException
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class BrowserFactory:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.browser_factory")

    @classmethod
    def launch_browser(cls, playwright: Playwright, config_manager: ConfigManager) -> Browser:
        if config_manager.is_remote_execution():
            raise DriverInitializationException(
                "Remote execution is configured, but only local Playwright execution is enabled "
                "in Phase 2."
            )

        try:
            playwright_browser_name = config_manager.get_playwright_browser_name()
            launch_options = BrowserOptionsFactory.build_launch_options(config_manager)

            cls.LOGGER.info(
                "Launching local Playwright browser. Framework browser=%s | Playwright browser=%s",
                config_manager.get_browser(),
                playwright_browser_name,
            )

            if playwright_browser_name == "chromium":
                browser = playwright.chromium.launch(**launch_options)
            elif playwright_browser_name == "firefox":
                launch_options.pop("channel", None)
                browser = playwright.firefox.launch(**launch_options)
            else:
                raise DriverInitializationException(
                    f"Unsupported Playwright browser name resolved: {playwright_browser_name}"
                )

            cls.LOGGER.info("Browser launched successfully.")
            return browser

        except Exception as exc:
            raise DriverInitializationException("Failed to launch Playwright browser.") from exc