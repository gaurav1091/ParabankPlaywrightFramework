import re
from pathlib import Path

from playwright.sync_api import Locator, Page

from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.reports.report_path_manager import ReportPathManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class ScreenshotUtils:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.screenshot_utils")

    @staticmethod
    def _sanitize_name(name: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", name)

    @classmethod
    def build_screenshot_path(cls, screenshot_name: str) -> str:
        ReportPathManager.create_directory_if_not_exists(FrameworkConstants.SCREENSHOTS_FOLDER)
        safe_name = cls._sanitize_name(screenshot_name)
        return str(Path(FrameworkConstants.SCREENSHOTS_FOLDER) / f"{safe_name}.png")

    @classmethod
    def capture_page_screenshot(cls, page: Page, screenshot_name: str, full_page: bool = True) -> str:
        path = cls.build_screenshot_path(screenshot_name)
        page.screenshot(path=path, full_page=full_page)
        cls.LOGGER.info("Captured page screenshot: %s", path)
        return path

    @classmethod
    def capture_locator_screenshot(cls, locator: Locator, screenshot_name: str) -> str:
        path = cls.build_screenshot_path(screenshot_name)
        locator.screenshot(path=path)
        cls.LOGGER.info("Captured locator screenshot: %s", path)
        return path
