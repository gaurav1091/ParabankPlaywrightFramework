from pytest_bdd import then, when

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.login_test_data_provider import LoginTestDataProvider
from com.parabank.automation.pages.login_page import LoginPage


@when("the user logs in with valid credentials")
def login_with_valid_credentials(test_context: FrameworkContext) -> None:
    login_page = test_context.scenario_context.get("login_page")
    if login_page is None:
        login_page = LoginPage(test_context.page, test_context.config_manager)

    login_test_data = LoginTestDataProvider.get_login_test_data_by_key("validUser")

    home_page = login_page.login(
        login_test_data.username,
        login_test_data.password,
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
        "login_logout_link_visibility",
    )
    UiAssertions.assert_element_visible(
        test_context.page,
        home_page.is_left_panel_visible(),
        "Left Panel",
        "Left panel should be visible after successful login.",
        "login_left_panel_visibility",
    )