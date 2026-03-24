from playwright.sync_api import Page

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.pages.framework_sanity_page import FrameworkSanityPage


def test_base_page_and_ui_utilities_work(
    framework_page: Page,
    framework_config: ConfigManager,
) -> None:
    sanity_page = FrameworkSanityPage(framework_page, framework_config)

    sanity_page.open_application()

    assert "ParaBank" in sanity_page.get_title()
    assert sanity_page.is_logo_visible() is True
    assert sanity_page.is_left_panel_visible() is True
    assert sanity_page.is_customer_login_title_visible() is True

    screenshot_path = sanity_page.capture_screenshot("phase3_framework_sanity_page")
    diagnostics = sanity_page.capture_failure_diagnostics("phase3_framework_sanity_page_diagnostics")

    assert screenshot_path.endswith(".png")
    assert diagnostics["screenshot_path"].endswith(".png")
    assert diagnostics["url"].startswith("https://")
    assert "ParaBank" in diagnostics["title"]