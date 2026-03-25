import pytest
from playwright.sync_api import Page

from com.parabank.automation.config.config_manager import ConfigManager


pytestmark = [pytest.mark.sanity, pytest.mark.ui]


def test_local_browser_launches_and_opens_parabank(
    framework_page: Page,
    framework_config: ConfigManager,
) -> None:
    framework_page.goto(
        framework_config.get_base_url(),
        wait_until="domcontentloaded",
        timeout=framework_config.get_playwright_navigation_timeout_millis(),
    )

    assert "ParaBank" in framework_page.title()