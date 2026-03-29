import pytest

from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.pages.login_page import LoginPage


@pytest.mark.hybrid
@pytest.mark.regression
@pytest.mark.ui
def test_invalid_login_should_not_allow_api_usage(test_context) -> None:
    context = test_context

    login_page = LoginPage(context.page, context.config_manager)
    login_page.open_login_page()
    login_page.login("invalid_user", "invalid_pass")

    UiAssertions.assert_element_visible(
        context.page,
        login_page.is_error_message_visible(),
        "Invalid Login Error Message",
        "Expected invalid login error message to be visible.",
        "hybrid_invalid_login_error_visible",
    )

    error_message = login_page.get_error_message()
    UiAssertions.assert_text_not_empty(
        context.page,
        error_message,
        "Expected non-empty invalid login error message.",
        "hybrid_invalid_login_error_text",
    )

    UiAssertions.assert_current_url_not_contains(
        context.page,
        "overview",
        "User should not navigate to an authenticated page after invalid login.",
        "hybrid_invalid_login_url_check",
    )
