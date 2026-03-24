from playwright.sync_api import Page

from com.parabank.automation.config.config_manager import ConfigManager


def test_local_browser_launches_and_opens_parabank(
    framework_page: Page,
    framework_config: ConfigManager,
) -> None:
    framework_page.goto(framework_config.get_base_url())
    assert "ParaBank" in framework_page.title()