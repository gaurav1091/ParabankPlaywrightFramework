from playwright.sync_api import Locator, Page

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.enums.wait_strategy import WaitStrategy
from com.parabank.automation.exceptions.element_operation_exception import ElementOperationException
from com.parabank.automation.utils.framework_logger import FrameworkLogger
from com.parabank.automation.utils.wait_utils import WaitUtils


class ElementUtils:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.element_utils")

    def __init__(self, page: Page, config_manager: ConfigManager) -> None:
        self.page = page
        self.config_manager = config_manager

    def get_locator(self, selector: str) -> Locator:
        self.LOGGER.info("Resolving locator for selector: %s", selector)
        return self.page.locator(selector)

    def wait_for_visible(self, selector: str) -> Locator:
        locator = self.get_locator(selector)
        return WaitUtils.wait_for_locator(
            locator,
            WaitStrategy.VISIBLE,
            self.config_manager.get_explicit_wait() * 1000,
        )

    def wait_for_hidden(self, selector: str) -> Locator:
        locator = self.get_locator(selector)
        return WaitUtils.wait_for_locator(
            locator,
            WaitStrategy.HIDDEN,
            self.config_manager.get_explicit_wait() * 1000,
        )

    def click(self, selector: str) -> None:
        try:
            locator = self.wait_for_visible(selector)
            self.LOGGER.info("Clicking selector: %s", selector)
            locator.click(timeout=self.config_manager.get_playwright_action_timeout_millis())
        except Exception as exc:
            raise ElementOperationException(f"Failed to click selector: {selector}") from exc

    def fill(self, selector: str, value: str) -> None:
        try:
            locator = self.wait_for_visible(selector)
            self.LOGGER.info("Filling selector: %s | Value: %s", selector, value)
            locator.fill(value, timeout=self.config_manager.get_playwright_action_timeout_millis())
        except Exception as exc:
            raise ElementOperationException(f"Failed to fill selector: {selector}") from exc

    def get_text(self, selector: str) -> str:
        try:
            locator = self.wait_for_visible(selector)
            text = locator.text_content(timeout=self.config_manager.get_playwright_action_timeout_millis()) or ""
            normalized = text.strip()
            self.LOGGER.info("Read text from selector: %s | Value: %s", selector, normalized)
            return normalized
        except Exception as exc:
            raise ElementOperationException(f"Failed to get text for selector: {selector}") from exc

    def is_visible(self, selector: str) -> bool:
        try:
            visible = self.get_locator(selector).is_visible(
                timeout=self.config_manager.get_playwright_action_timeout_millis()
            )
            self.LOGGER.info("Visibility for selector: %s | Visible: %s", selector, visible)
            return visible
        except Exception:
            return False

    def get_count(self, selector: str) -> int:
        try:
            count = self.get_locator(selector).count()
            self.LOGGER.info("Count for selector: %s | Count: %s", selector, count)
            return count
        except Exception as exc:
            raise ElementOperationException(f"Failed to get count for selector: {selector}") from exc

    def hover(self, selector: str) -> None:
        try:
            locator = self.wait_for_visible(selector)
            self.LOGGER.info("Hovering selector: %s", selector)
            locator.hover(timeout=self.config_manager.get_playwright_action_timeout_millis())
        except Exception as exc:
            raise ElementOperationException(f"Failed to hover selector: {selector}") from exc

    def press(self, selector: str, key: str) -> None:
        try:
            locator = self.wait_for_visible(selector)
            self.LOGGER.info("Pressing key on selector: %s | Key: %s", selector, key)
            locator.press(key, timeout=self.config_manager.get_playwright_action_timeout_millis())
        except Exception as exc:
            raise ElementOperationException(f"Failed to press key '{key}' on selector: {selector}") from exc
