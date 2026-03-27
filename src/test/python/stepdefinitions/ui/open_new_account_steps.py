from pytest_bdd import then, when, parsers

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.login_test_data_provider import LoginTestDataProvider
from com.parabank.automation.dataproviders.open_new_account_test_data_provider import OpenNewAccountTestDataProvider
from com.parabank.automation.pages.login_page import LoginPage


@when("the user navigates to the Open New Account page")
def navigate_to_open_new_account_page(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before navigating to Open New Account page.",
    )

    open_new_account_page = home_page.go_to_open_new_account()
    test_context.scenario_context.set("open_new_account_page", open_new_account_page)


@then("the Open New Account page should be displayed")
def verify_open_new_account_page_displayed(test_context: FrameworkContext) -> None:
    open_new_account_page = test_context.scenario_context.get("open_new_account_page")
    CommonAssertions.assert_not_none(
        open_new_account_page,
        "Open New Account page should be available in scenario context.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        open_new_account_page.is_open_new_account_page_loaded(),
        "Open New Account Page",
        "Open New Account page is not displayed.",
        "open_new_account_page_loaded",
    )
    UiAssertions.assert_text_equals(
        test_context.page,
        open_new_account_page.get_page_heading_text(),
        "Open New Account",
        "Open New Account page title is incorrect.",
        "open_new_account_title",
    )


@when(parsers.parse('the user creates a new account using test data key "{test_data_key}"'))
def create_new_account_using_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    open_new_account_page = test_context.scenario_context.get("open_new_account_page")
    CommonAssertions.assert_not_none(
        open_new_account_page,
        "Open New Account page should be available before account creation.",
    )

    open_new_account_test_data = OpenNewAccountTestDataProvider.get_open_new_account_test_data_by_key(test_data_key)
    test_context.scenario_context.set("open_new_account_test_data", open_new_account_test_data)

    open_new_account_page = open_new_account_page.open_new_account(open_new_account_test_data.account_type)
    test_context.scenario_context.set("open_new_account_page", open_new_account_page)


@then("the new account should be created successfully")
def verify_new_account_created_successfully(test_context: FrameworkContext) -> None:
    open_new_account_page = test_context.scenario_context.get("open_new_account_page")
    CommonAssertions.assert_not_none(
        open_new_account_page,
        "Open New Account page should be available for success validation.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        open_new_account_page.is_account_creation_successful(),
        "Account Opened Confirmation",
        "New account was not created successfully.",
        "open_new_account_success",
    )
    UiAssertions.assert_text_equals(
        test_context.page,
        open_new_account_page.get_account_opened_heading_text(),
        "Account Opened!",
        "Account creation success title is incorrect.",
        "open_new_account_success_title",
    )


@then("the new account number should be displayed")
def verify_new_account_number_displayed(test_context: FrameworkContext) -> None:
    open_new_account_page = test_context.scenario_context.get("open_new_account_page")
    CommonAssertions.assert_not_none(
        open_new_account_page,
        "Open New Account page should be available for account number validation.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        open_new_account_page.is_new_account_number_visible(),
        "New Account Number",
        "New account number is not displayed.",
        "open_new_account_number_visible",
    )

    new_account_number = open_new_account_page.get_new_account_number().strip()
    CommonAssertions.assert_true(
        len(new_account_number) > 0,
        "New account number should not be empty.",
    )
    test_context.scenario_context.set("new_account_number", new_account_number)