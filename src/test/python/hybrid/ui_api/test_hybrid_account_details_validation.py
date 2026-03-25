import pytest
from playwright.sync_api import Page, Playwright

from com.parabank.automation.api.services.accounts_api_service import AccountsApiService
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.hybrid.services.hybrid_accounts_service import HybridAccountsService
from com.parabank.automation.pages.login_page import LoginPage
from com.parabank.automation.utils.data_provider import DataProvider


pytestmark = [pytest.mark.hybrid, pytest.mark.ui, pytest.mark.api, pytest.mark.integration, pytest.mark.regression]


def test_accounts_overview_ui_vs_api_validation(
    framework_page: Page,
    framework_playwright: Playwright,
    framework_config: ConfigManager,
) -> None:
    context = FrameworkContext(framework_page, framework_config)
    context.reset_hybrid_state()

    login_data = DataProvider.get_login_data(
        "login/login_test_data.json",
        "validLogin",
    )

    login_page = LoginPage(framework_page, framework_config)

    login_page.open_login_page()
    home_page = login_page.login(login_data.username, login_data.password)

    accounts_overview_page = home_page.go_to_accounts_overview()

    api_service = AccountsApiService(framework_playwright, framework_config)

    try:
        hybrid_service = HybridAccountsService(accounts_overview_page, api_service)

        hybrid_service.load_ui_data(context)
        hybrid_service.load_api_data(context)
        hybrid_service.validate_ui_vs_api(context)

    finally:
        api_service.dispose()