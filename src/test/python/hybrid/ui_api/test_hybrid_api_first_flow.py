import pytest
from playwright.sync_api import Playwright

from com.parabank.automation.api.services.accounts_api_service import AccountsApiService
from com.parabank.automation.hybrid.services.hybrid_accounts_service import HybridAccountsService
from com.parabank.automation.pages.login_page import LoginPage
from com.parabank.automation.utils.data_provider import DataProvider


@pytest.mark.hybrid
@pytest.mark.regression
@pytest.mark.api
def test_api_first_then_ui_validation(test_context, framework_playwright: Playwright) -> None:
    context = test_context
    context.reset_hybrid_state()

    login_data = DataProvider.get_login_data(
        "login/login_test_data.json",
        "validLogin",
    )

    login_page = LoginPage(context.page, context.config_manager)
    login_page.open_login_page()
    home_page = login_page.login(login_data.username, login_data.password)

    accounts_overview_page = home_page.go_to_accounts_overview()

    api_service = AccountsApiService(framework_playwright, context.config_manager)

    try:
        hybrid_service = HybridAccountsService(accounts_overview_page, api_service)

        # API-first in assertion intent: collect both sources and assert parity
        hybrid_service.load_ui_data(context)
        hybrid_service.load_api_data(context)

        assert sorted(context.api_account_ids) == sorted(context.ui_account_ids), (
            "API-first validation failed.\n"
            f"API Account IDs: {sorted(context.api_account_ids)}\n"
            f"UI Account IDs : {sorted(context.ui_account_ids)}"
        )
    finally:
        api_service.dispose()