import os
import platform

from playwright.sync_api import Browser, Playwright

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.exceptions.driver_initialization_exception import DriverInitializationException
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class BrowserFactory:
    _LOGGER = FrameworkLogger.get_logger("parabank_framework.browser_factory")

    @staticmethod
    def launch_browser(playwright: Playwright, config_manager: ConfigManager) -> Browser:
        try:
            framework_browser = config_manager.get_browser()
            playwright_browser_name = config_manager.get_playwright_browser_name()
            playwright_channel = config_manager.get_playwright_browser_channel()

            disable_channel_flag = os.getenv("DISABLE_PLAYWRIGHT_BROWSER_CHANNEL", "false").strip().lower() in {
                "true",
                "1",
                "yes",
                "y",
                "on",
            }

            current_system = platform.system().lower()
            current_machine = platform.machine().lower()

            is_linux_arm = current_system == "linux" and current_machine in {"aarch64", "arm64"}

            if disable_channel_flag or is_linux_arm:
                playwright_channel = None

            BrowserFactory._LOGGER.info(
                "Launching local Playwright browser. Framework browser=%s | Playwright browser=%s | Channel=%s",
                framework_browser,
                playwright_browser_name,
                playwright_channel if playwright_channel else "bundled-default",
            )

            launch_options = {
                "headless": config_manager.is_headless(),
                "slow_mo": config_manager.get_playwright_slow_mo_millis(),
                "timeout": config_manager.get_playwright_browser_launch_timeout_millis(),
            }

            if playwright_channel:
                launch_options["channel"] = playwright_channel

            if playwright_browser_name == "chromium":
                browser = playwright.chromium.launch(**launch_options)
            elif playwright_browser_name == "firefox":
                browser = playwright.firefox.launch(**launch_options)
            elif playwright_browser_name == "webkit":
                browser = playwright.webkit.launch(**launch_options)
            else:
                raise DriverInitializationException(
                    f"Unsupported Playwright browser type resolved from config: {playwright_browser_name}"
                )

            BrowserFactory._LOGGER.info("Browser launched successfully.")
            return browser

        except Exception as exc:
            raise DriverInitializationException("Failed to launch Playwright browser.") from exc