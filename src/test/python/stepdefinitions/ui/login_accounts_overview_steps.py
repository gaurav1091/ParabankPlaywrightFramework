from pytest_bdd import given, then, when

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.pages.login_page import LoginPage


@given("the user opens the Parabank login page")
def open_login_page(test_context: FrameworkContext) -> None:
    login_page = LoginPage(test_context.page, test_context.config_manager)
    login_page.open_login_page()
    test_context.scenario_context.set("login_page", login_page)


@when("the user logs in with valid credentials")
def login_with_valid_credentials(test_context: FrameworkContext) -> None:
    login_page = test_context.scenario_context.get("login_page")
    if login_page is None:
        login_page = LoginPage(test_context.page, test_context.config_manager)

    home_page = login_page.login(
        test_context.config_manager.get_username(),
        test_context.config_manager.get_password(),
    )
    test_context.scenario_context.set("home_page", home_page)


@then("the user should be successfully logged in")
def verify_successful_login(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available in scenario context after login.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        home_page.is_logout_link_visible(),
        "Log Out Link",
        "Logout link should be visible after successful login.",
        "phase8_logout_link_visibility",
    )
    UiAssertions.assert_element_visible(
        test_context.page,
        home_page.is_left_panel_visible(),
        "Left Panel",
        "Left panel should be visible after successful login.",
        "phase8_left_panel_visibility",
    )


@then("the accounts overview page should be displayed")
def verify_accounts_overview_displayed(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    accounts_overview_page = home_page.go_to_accounts_overview()

    test_context.scenario_context.set("accounts_overview_page", accounts_overview_page)

    UiAssertions.assert_page_title_contains(
        test_context.page,
        "ParaBank",
        "Accounts Overview page title validation failed.",
        "phase8_accounts_overview_title",
    )
    UiAssertions.assert_current_url_contains(
        test_context.page,
        "overview",
        "Accounts Overview URL validation failed.",
        "phase8_accounts_overview_url",
    )
    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_page_heading_visible(),
        "Accounts Overview Heading",
        "Accounts Overview heading should be visible.",
        "phase8_accounts_overview_heading",
    )


@then("the accounts table should contain at least one account")
def verify_accounts_table_contains_at_least_one_account(test_context: FrameworkContext) -> None:
    accounts_overview_page = test_context.scenario_context.get("accounts_overview_page")

    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_table_visible(),
        "Accounts Table",
        "Accounts table should be visible on Accounts Overview page.",
        "phase8_accounts_table_visibility",
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