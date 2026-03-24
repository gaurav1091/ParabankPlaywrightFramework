from playwright.sync_api import Page

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
        WaitUtils.wait_for_page_load(self.page, self.config_manager)

    def open_base_url(self) -> None:
        self.logger.info("Opening base URL.")
        self.open(self.config_manager.get_base_url())

    def get_title(self) -> str:
        title = self.page.title()
        self.logger.info("Current page title: %s", title)
        return title

    def get_current_url(self) -> str:
        url = self.page.url
        self.logger.info("Current page URL: %s", url)
        return url

    def click(self, selector: str) -> None:
        self.element_utils.click(selector)

    def enter_text(self, selector: str, value: str) -> None:
        self.element_utils.fill(selector, value)

    def get_text(self, selector: str) -> str:
        return self.element_utils.get_text(selector)

    def is_visible(self, selector: str) -> bool:
        return self.element_utils.is_visible(selector)

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

    def capture_screenshot(self, screenshot_name: str) -> str:
        return ScreenshotUtils.capture_page_screenshot(self.page, screenshot_name, full_page=True)

    def capture_failure_diagnostics(self, diagnostic_name: str) -> dict[str, str]:
        return FailureDiagnosticsUtils.capture_page_diagnostics(self.page, diagnostic_name)