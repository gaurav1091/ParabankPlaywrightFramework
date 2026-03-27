from pytest_bdd import given

from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.pages.login_page import LoginPage


@given("the user opens the Parabank login page")
def open_login_page(test_context: FrameworkContext) -> None:
    login_page = LoginPage(test_context.page, test_context.config_manager)
    login_page.open_login_page()
    test_context.scenario_context.set("login_page", login_page)