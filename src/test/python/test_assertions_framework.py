import pytest
from playwright.sync_api import Page

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.pages.framework_sanity_page import FrameworkSanityPage


pytestmark = [pytest.mark.sanity, pytest.mark.ui]


def test_common_and_ui_assertions_work(
    framework_page: Page,
    framework_config: ConfigManager,
) -> None:
    sanity_page = FrameworkSanityPage(framework_page, framework_config)
    sanity_page.open_application()

    title = sanity_page.get_title()
    url = sanity_page.get_current_url()
    logo_visible = sanity_page.is_logo_visible()
    left_panel_visible = sanity_page.is_left_panel_visible()

    CommonAssertions.assert_not_none(
        title,
        "Page title should not be None after opening the application.",
    )
    CommonAssertions.assert_contains(
        title,
        "ParaBank",
        "Page title should contain ParaBank after opening the application.",
    )
    CommonAssertions.assert_true(
        left_panel_visible,
        "Left panel should be visible on the ParaBank landing page.",
    )
    CommonAssertions.assert_true(
        logo_visible,
        "ParaBank logo should be visible on the ParaBank landing page.",
    )

    UiAssertions.assert_page_title_contains(
        framework_page,
        "ParaBank",
        "Landing page title validation failed.",
        "phase4_title_assertion",
    )
    UiAssertions.assert_current_url_contains(
        framework_page,
        "parabank",
        "Landing page URL validation failed.",
        "phase4_url_assertion",
    )
    UiAssertions.assert_element_visible(
        framework_page,
        logo_visible,
        "ParaBank Logo",
        "ParaBank logo should be visible.",
        "phase4_logo_visibility_assertion",
    )
    UiAssertions.assert_element_visible(
        framework_page,
        left_panel_visible,
        "Left Panel",
        "Left panel should be visible.",
        "phase4_left_panel_visibility_assertion",
    )
    UiAssertions.assert_text_equals(
        framework_page,
        url,
        framework_page.url,
        "Current URL text comparison failed.",
        "phase4_url_text_assertion",
    )