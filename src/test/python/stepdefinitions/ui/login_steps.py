from __future__ import annotations

from pytest_bdd import parsers, then, when

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.login_test_data_provider import LoginTestDataProvider
from com.parabank.automation.pages.login_page import LoginPage


def _get_or_create_login_page(test_context: FrameworkContext) -> LoginPage:
    login_page = test_context.scenario_context.get("login_page")
    if isinstance(login_page, LoginPage):
        return login_page

    login_page = LoginPage(test_context.page, test_context.config_manager)
    test_context.scenario_context.set("login_page", login_page)
    return login_page


@when("the user logs in with valid credentials")
def login_with_valid_credentials(test_context: FrameworkContext) -> None:
    login_page = _get_or_create_login_page(test_context)
    login_test_data = LoginTestDataProvider.get_login_test_data_by_key("validUser")

    home_page = login_page.login(
        login_test_data.username,
        login_test_data.password,
    )
    test_context.scenario_context.set("home_page", home_page)


@when(parsers.parse('the user logs in with valid test data key "{test_data_key}"'))
def login_with_valid_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    login_page = _get_or_create_login_page(test_context)
    login_test_data = LoginTestDataProvider.get_login_test_data_by_key(test_data_key)

    home_page = login_page.login(
        login_test_data.username,
        login_test_data.password,
    )
    test_context.scenario_context.set("home_page", home_page)


@when(parsers.parse('the user attempts login failure with test data key "{test_data_key}"'))
def login_failure_with_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    login_page = _get_or_create_login_page(test_context)
    login_test_data = LoginTestDataProvider.get_login_test_data_by_key(test_data_key)

    login_page = login_page.login_expecting_failure(
        login_test_data.username,
        login_test_data.password,
    )
    test_context.scenario_context.set("login_page", login_page)
    test_context.scenario_context.set("home_page", None)


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
        "login_logout_link_visibility",
    )
    UiAssertions.assert_element_visible(
        test_context.page,
        home_page.is_left_panel_visible(),
        "Left Panel",
        "Left panel should be visible after successful login.",
        "login_left_panel_visibility",
    )


@then("the user should be navigated to the home page")
def verify_home_page_navigation(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available in scenario context after login.",
    )

    UiAssertions.assert_current_url_contains(
        test_context.page,
        "overview",
        "User should be navigated to the authenticated home page after login.",
        "login_home_page_url_validation",
    )
    UiAssertions.assert_element_visible(
        test_context.page,
        home_page.is_left_panel_visible(),
        "Left Panel",
        "Left panel should be visible on the home page after login.",
        "login_home_page_left_panel_visibility",
    )


@then("the logout link should be visible")
def verify_logout_link_visibility(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available in scenario context before validating logout link visibility.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        home_page.is_logout_link_visible(),
        "Log Out Link",
        "Logout link should be visible after successful login.",
        "login_logout_link_visibility_java_parity",
    )


@then("the user should see the login error message")
def verify_login_error_message(test_context: FrameworkContext) -> None:
    login_page = test_context.scenario_context.get("login_page")
    CommonAssertions.assert_not_none(
        login_page,
        "Login page should remain available in scenario context after failed login.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        login_page.is_error_message_visible(),
        "Invalid Login Error Message",
        "Login error message should be visible after invalid login attempt.",
        "login_error_message_visibility",
    )

    actual_error_message = login_page.get_error_message()
    UiAssertions.assert_text_not_empty(
        test_context.page,
        actual_error_message,
        "Login error message should not be empty after invalid login attempt.",
        "login_error_message_not_empty",
    )

    UiAssertions.assert_current_url_not_contains(
        test_context.page,
        "overview",
        "User should not navigate to an authenticated page after invalid login.",
        "login_invalid_user_should_remain_unauthenticated",
    )