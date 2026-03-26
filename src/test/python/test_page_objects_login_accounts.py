import pytest
from playwright.sync_api import Page

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.pages.login_page import LoginPage


pytestmark = [pytest.mark.ui, pytest.mark.regression]


def test_login_home_and_accounts_overview_page_objects_work(
    framework_page: Page,
    framework_config: ConfigManager,
) -> None:
    login_page = LoginPage(framework_page, framework_config)
    login_page.open_login_page()

    UiAssertions.assert_element_visible(
        framework_page,
        login_page.is_username_field_visible(),
        "Username Field",
        "Username field should be visible on login page.",
        "phase6_username_field_visibility",
    )
    UiAssertions.assert_element_visible(
        framework_page,
        login_page.is_password_field_visible(),
        "Password Field",
        "Password field should be visible on login page.",
        "phase6_password_field_visibility",
    )
    UiAssertions.assert_element_visible(
        framework_page,
        login_page.is_login_button_visible(),
        "Login Button",
        "Login button should be visible on login page.",
        "phase6_login_button_visibility",
    )

    home_page = login_page.login(
        framework_config.get_username(),
        framework_config.get_password(),
    )

    UiAssertions.assert_element_visible(
        framework_page,
        home_page.is_logout_link_visible(),
        "Log Out Link",
        "Logout link should be visible after successful login.",
        "phase6_logout_link_visibility",
    )
    UiAssertions.assert_element_visible(
        framework_page,
        home_page.is_accounts_overview_link_visible(),
        "Accounts Overview Link",
        "Accounts Overview link should be visible after successful login.",
        "phase6_accounts_overview_link_visibility",
    )
    UiAssertions.assert_element_visible(
        framework_page,
        home_page.is_left_panel_visible(),
        "Left Panel",
        "Left panel should be visible after successful login.",
        "phase6_left_panel_visibility",
    )

    accounts_overview_page = home_page.go_to_accounts_overview()

    UiAssertions.assert_page_title_contains(
        framework_page,
        "ParaBank",
        "Accounts Overview page title validation failed.",
        "phase6_accounts_overview_title",
    )
    UiAssertions.assert_current_url_contains(
        framework_page,
        "overview",
        "Accounts Overview URL validation failed.",
        "phase6_accounts_overview_url",
    )
    UiAssertions.assert_element_visible(
        framework_page,
        accounts_overview_page.is_page_heading_visible(),
        "Accounts Overview Heading",
        "Accounts Overview heading should be visible.",
        "phase6_accounts_overview_heading",
    )
    UiAssertions.assert_element_visible(
        framework_page,
        accounts_overview_page.is_accounts_table_visible(),
        "Accounts Table",
        "Accounts table should be visible on Accounts Overview page.",
        "phase6_accounts_table_visibility",
    )

    CommonAssertions.assert_equals(
        accounts_overview_page.get_page_heading_text(),
        "Accounts Overview",
        "Accounts Overview heading text should match expected value.",
    )

    account_row_count = accounts_overview_page.get_account_row_count()
    account_link_count = accounts_overview_page.get_account_link_count()

    CommonAssertions.assert_greater_than(
        account_row_count,
        0,
        "Accounts table should contain at least one row.",
    )
    CommonAssertions.assert_greater_than(
        account_link_count,
        0,
        "Accounts table should contain at least one account link.",
    )