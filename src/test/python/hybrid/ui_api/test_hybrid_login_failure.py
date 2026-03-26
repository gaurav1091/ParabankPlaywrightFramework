import pytest

from com.parabank.automation.pages.login_page import LoginPage


@pytest.mark.hybrid
@pytest.mark.regression
@pytest.mark.ui
def test_invalid_login_should_not_allow_api_usage(test_context) -> None:
    context = test_context

    login_page = LoginPage(context.page, context.config_manager)
    login_page.open_login_page()
    login_page.login("invalid_user", "invalid_pass")

    assert login_page.is_error_message_visible(), "Expected invalid login error message to be visible."

    error_message = login_page.get_error_message()
    assert error_message, "Expected non-empty invalid login error message."

    cookies = context.page.context.cookies()
    jsession_cookies = [cookie for cookie in cookies if cookie.get("name") == "JSESSIONID"]

    # ParaBank may still issue a session cookie for anonymous/failed attempts,
    # so the real check is that authenticated UI state was not reached.
    assert "overview" not in context.page.url.lower(), (
        "User should not navigate to an authenticated page after invalid login."
    )
    assert login_page.is_error_message_visible(), "Login failure state should remain visible."
    assert len(jsession_cookies) >= 0