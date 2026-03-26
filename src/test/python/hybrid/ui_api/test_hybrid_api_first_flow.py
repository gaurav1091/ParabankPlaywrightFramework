import pytest
from playwright.sync_api import Playwright

from com.parabank.automation.api.services.accounts_api_service import AccountsApiService
from com.parabank.automation.hybrid.services.hybrid_accounts_service import HybridAccountsService
from com.parabank.automation.pages.login_page import LoginPage


@pytest.mark.hybrid
@pytest.mark.regression
@pytest.mark.api
def test_api_first_then_ui_validation(test_context, framework_playwright: Playwright) -> None:
    context = test_context
    context.reset_hybrid_state()

    login_page = LoginPage(context.page, context.config_manager)
    login_page.open_login_page()
    home_page = login_page.login(
        context.config_manager.get_username(),
        context.config_manager.get_password(),
    )

    accounts_overview_page = home_page.go_to_accounts_overview()

    api_service = AccountsApiService(framework_playwright, context.config_manager)

    try:
        hybrid_service = HybridAccountsService(accounts_overview_page, api_service)
        hybrid_service.load_ui_data(context)
        hybrid_service.load_api_data(context)

        assert sorted(context.api_account_ids) == sorted(context.ui_account_ids), (
            "API-first validation failed.\n"
            f"API Account IDs: {sorted(context.api_account_ids)}\n"
            f"UI Account IDs : {sorted(context.ui_account_ids)}"
        )
    finally:
        api_service.dispose()