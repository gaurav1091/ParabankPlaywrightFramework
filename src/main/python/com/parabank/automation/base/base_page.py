from __future__ import annotations

from playwright.sync_api import Locator, Page

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.element_utils import ElementUtils
from com.parabank.automation.utils.failure_diagnostics_utils import FailureDiagnosticsUtils
from com.parabank.automation.utils.framework_logger import FrameworkLogger
from com.parabank.automation.utils.screenshot_utils import ScreenshotUtils
from com.parabank.automation.utils.wait_utils import WaitUtils


class BasePage:
    def __init__(self, page: Page, config_manager: ConfigManager) -> None:
        self.page = page
        self.config_manager = config_manager
        self.element_utils = ElementUtils(page, config_manager)
        self.logger = FrameworkLogger.get_logger(self.__class__.__module__ + "." + self.__class__.__name__)

    def open(self, url: str) -> None:
        self.logger.info("Opening URL: %s", url)
        self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=self.config_manager.get_playwright_navigation_timeout_millis(),
        )
        self.wait_for_page_ready()

    def open_base_url(self) -> None:
        self.logger.info("Opening base URL.")
        self.open(self.config_manager.get_base_url())

    def wait_for_page_ready(self) -> None:
        WaitUtils.wait_for_page_load(self.page, self.config_manager)

    def get_title(self) -> str:
        title = self.page.title()
        self.logger.info("Current page title: %s", title)
        return title

    def get_current_url(self) -> str:
        url = self.page.url
        self.logger.info("Current page URL: %s", url)
        return url

    def get_locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def click(self, selector: str) -> None:
        self.element_utils.click(selector)

    def enter_text(self, selector: str, value: str) -> None:
        self.element_utils.fill(selector, value)

    def clear_and_enter_text(self, selector: str, value: str) -> None:
        self.logger.info("Clearing and entering text for selector: %s", selector)
        locator = self.get_locator(selector)
        locator.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        locator.clear(timeout=self.config_manager.get_playwright_action_timeout_millis())
        locator.fill(value, timeout=self.config_manager.get_playwright_action_timeout_millis())

    def get_text(self, selector: str) -> str:
        return self.element_utils.get_text(selector)

    def get_input_value(self, selector: str) -> str:
        locator = self.get_locator(selector)
        locator.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        value = (locator.input_value(timeout=self.config_manager.get_playwright_action_timeout_millis()) or "").strip()
        self.logger.info("Input value for selector: %s | Value: %s", selector, value)
        return value

    def is_visible(self, selector: str) -> bool:
        return self.element_utils.is_visible(selector)

    def is_enabled(self, selector: str) -> bool:
        try:
            enabled = self.get_locator(selector).is_enabled(
                timeout=self.config_manager.get_playwright_action_timeout_millis()
            )
            self.logger.info("Enabled state for selector: %s | Enabled: %s", selector, enabled)
            return enabled
        except Exception:
            return False

    def get_count(self, selector: str) -> int:
        return self.element_utils.get_count(selector)

    def hover(self, selector: str) -> None:
        self.element_utils.hover(selector)

    def press(self, selector: str, key: str) -> None:
        self.element_utils.press(selector, key)

    def wait_for_url_contains(self, partial_url: str) -> None:
        WaitUtils.wait_for_url_contains(
            self.page,
            partial_url,
            self.config_manager.get_playwright_navigation_timeout_millis(),
        )

    def select_dropdown_by_visible_text(self, selector: str, visible_text: str) -> None:
        self.logger.info("Selecting dropdown value by visible text. Selector=%s | Text=%s", selector, visible_text)
        locator = self.get_locator(selector)
        locator.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        locator.select_option(
            label=visible_text,
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )

    def select_dropdown_by_value(self, selector: str, value: str) -> None:
        self.logger.info("Selecting dropdown value by option value. Selector=%s | Value=%s", selector, value)
        locator = self.get_locator(selector)
        locator.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        locator.select_option(
            value=value,
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )

    def get_selected_dropdown_text(self, selector: str) -> str:
        locator = self.get_locator(selector)
        locator.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        selected_text = locator.locator("option:checked").inner_text().strip()
        self.logger.info("Selected dropdown text. Selector=%s | Text=%s", selector, selected_text)
        return selected_text

    def get_dropdown_options_text(self, selector: str) -> list[str]:
        locator = self.get_locator(selector)
        locator.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )

        options = locator.locator("option")
        count = options.count()

        values: list[str] = []
        for index in range(count):
            text = options.nth(index).inner_text().strip()
            if text:
                values.append(text)

        self.logger.info("Dropdown options for selector=%s | Options=%s", selector, values)
        return values

    def select_first_valid_dropdown_option(self, selector: str, ignore_texts: set[str] | None = None) -> str:
        ignored = {text.strip().lower() for text in (ignore_texts or set())}

        locator = self.get_locator(selector)
        locator.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )

        options = locator.locator("option")
        count = options.count()

        for index in range(count):
            option = options.nth(index)
            value = (option.get_attribute("value") or "").strip()
            text = option.inner_text().strip()

            if not value or not text:
                continue

            if text.lower() in ignored:
                continue

            locator.select_option(
                value=value,
                timeout=self.config_manager.get_playwright_action_timeout_millis(),
            )
            self.logger.info(
                "Selected first valid dropdown option. Selector=%s | Value=%s | Text=%s",
                selector,
                value,
                text,
            )
            return text

        raise RuntimeError(f"No valid dropdown option found for selector '{selector}'")

    def capture_screenshot(self, screenshot_name: str) -> str:
        return ScreenshotUtils.capture_page_screenshot(self.page, screenshot_name, full_page=True)

    def capture_failure_diagnostics(self, diagnostic_name: str) -> dict[str, str]:
        return FailureDiagnosticsUtils.capture_page_diagnostics(self.page, diagnostic_name)