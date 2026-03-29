import pytest
from playwright.sync_api import Playwright

from com.parabank.automation.api.services.accounts_api_service import AccountsApiService
from com.parabank.automation.assertions.api_assertions import ApiAssertions
from com.parabank.automation.hybrid.services.hybrid_accounts_service import HybridAccountsService
from com.parabank.automation.pages.login_page import LoginPage


@pytest.mark.hybrid
@pytest.mark.regression
def test_ui_api_mismatch_detection(test_context, framework_playwright: Playwright) -> None:
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

        ApiAssertions.assert_list_not_empty(
            context.ui_account_ids,
            "UI account list should not be empty for mismatch test.",
        )
        ApiAssertions.assert_list_not_empty(
            context.api_account_ids,
            "API account list should not be empty for mismatch test.",
        )

        mutated_api_ids = list(context.api_account_ids)
        if mutated_api_ids:
            mutated_api_ids = mutated_api_ids[:-1]
        else:
            mutated_api_ids = [999999999]

        ApiAssertions.assert_collections_do_not_match_ignoring_order(
            context.ui_account_ids,
            mutated_api_ids,
            "Mismatch should have been detected, but UI and manipulated API lists matched unexpectedly.",
        )
    finally:
        api_service.dispose()
