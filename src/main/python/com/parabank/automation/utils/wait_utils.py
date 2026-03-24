from playwright.sync_api import Locator, Page

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.enums.wait_strategy import WaitStrategy
from com.parabank.automation.exceptions.element_operation_exception import ElementOperationException
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class WaitUtils:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.wait_utils")

    @staticmethod
    def wait_for_page_load(page: Page, config_manager: ConfigManager) -> None:
        try:
            page.wait_for_load_state(
                "domcontentloaded",
                timeout=config_manager.get_playwright_navigation_timeout_millis(),
            )
            page.wait_for_load_state(
                "networkidle",
                timeout=config_manager.get_playwright_navigation_timeout_millis(),
            )
            WaitUtils.LOGGER.info("Page load completed successfully.")
        except Exception as exc:
            raise ElementOperationException("Failed while waiting for page load.") from exc

    @staticmethod
    def wait_for_locator(
        locator: Locator,
        strategy: WaitStrategy,
        timeout_millis: int,
    ) -> Locator:
        try:
            locator.wait_for(state=strategy.value, timeout=timeout_millis)
            WaitUtils.LOGGER.info(
                "Locator wait completed. Strategy=%s | TimeoutMillis=%s",
                strategy.value,
                timeout_millis,
            )
            return locator
        except Exception as exc:
            raise ElementOperationException(
                f"Failed waiting for locator with strategy '{strategy.value}'."
            ) from exc

    @staticmethod
    def wait_for_url_contains(
        page: Page,
        partial_url: str,
        timeout_millis: int,
    ) -> None:
        try:
            page.wait_for_url(f"**{partial_url}**", timeout=timeout_millis)
            WaitUtils.LOGGER.info(
                "Page URL contains expected value: %s",
                partial_url,
            )
        except Exception as exc:
            raise ElementOperationException(
                f"Failed waiting for URL to contain: {partial_url}"
            ) from exc

    @staticmethod
    def wait_for_timeout(timeout_millis: int) -> None:
        try:
            WaitUtils.LOGGER.info("Waiting for timeout millis: %s", timeout_millis)
        except Exception:
            pass