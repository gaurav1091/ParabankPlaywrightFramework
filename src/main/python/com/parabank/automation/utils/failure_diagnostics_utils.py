from playwright.sync_api import Page

from com.parabank.automation.utils.framework_logger import FrameworkLogger
from com.parabank.automation.utils.screenshot_utils import ScreenshotUtils


class FailureDiagnosticsUtils:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.failure_diagnostics")

    @classmethod
    def capture_page_diagnostics(
        cls,
        page: Page,
        diagnostic_name: str,
    ) -> dict[str, str]:
        screenshot_path = ScreenshotUtils.capture_page_screenshot(page, diagnostic_name, full_page=True)

        diagnostics = {
            "screenshot_path": screenshot_path,
            "url": page.url,
            "title": page.title(),
        }

        cls.LOGGER.info(
            "Captured page diagnostics. Screenshot=%s | URL=%s | Title=%s",
            diagnostics["screenshot_path"],
            diagnostics["url"],
            diagnostics["title"],
        )
        return diagnostics
