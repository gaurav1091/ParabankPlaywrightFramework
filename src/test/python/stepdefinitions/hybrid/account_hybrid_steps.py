from __future__ import annotations

from pytest_bdd import given, parsers, then, when
from playwright.sync_api import Playwright

from com.parabank.automation.api.services.accounts_api_service import AccountsApiService
from com.parabank.automation.assertions.api_assertions import ApiAssertions
from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.hybrid_account_validation_test_data_provider import (
    HybridAccountValidationTestDataProvider,
)
from com.parabank.automation.dataproviders.login_test_data_provider import LoginTestDataProvider
from com.parabank.automation.pages.login_page import LoginPage
from com.parabank.automation.utils.cookie_utils import CookieUtils
from com.parabank.automation.utils.customer_utils import CustomerUtils


HYBRID_ACCOUNTS_API_SERVICE_CONTEXT_KEY = "hybrid_accounts_api_service"


def _get_or_create_accounts_api_service(
    test_context: FrameworkContext,
    framework_playwright: Playwright,
    request,
) -> AccountsApiService:
    existing_service = test_context.scenario_context.get(HYBRID_ACCOUNTS_API_SERVICE_CONTEXT_KEY)
    if isinstance(existing_service, AccountsApiService):
        return existing_service

    service = AccountsApiService(framework_playwright, test_context.config_manager)
    test_context.scenario_context.set(HYBRID_ACCOUNTS_API_SERVICE_CONTEXT_KEY, service)
    request.addfinalizer(service.dispose)
    return service


@given(parsers.parse('user performs hybrid login with test data key "{test_data_key}"'))
def user_performs_hybrid_login_with_test_data_key(
    test_context: FrameworkContext,
    test_data_key: str,
) -> None:
    test_context.scenario_context.clear()
    test_context.reset_hybrid_state()

    hybrid_test_data = HybridAccountValidationTestDataProvider.get_hybrid_account_validation_test_data_by_key(
        test_data_key
    )
    login_test_data = LoginTestDataProvider.get_login_test_data_by_key(hybrid_test_data.login_key)

    login_page = LoginPage(test_context.page, test_context.config_manager)
    login_page.open_login_page()

    UiAssertions.assert_element_visible(
        test_context.page,
        login_page.is_login_page_displayed(),
        "Login Page",
        "Login page is not displayed for hybrid account validation flow.",
        "hybrid_account_validation_login_page_displayed",
    )

    home_page = login_page.login(
        login_test_data.username,
        login_test_data.password,
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        home_page.is_home_page_loaded(),
        "Home Page",
        "Home page is not displayed after hybrid account validation login.",
        "hybrid_account_validation_home_page_loaded",
    )

    test_context.scenario_context.set("home_page", home_page)
    test_context.scenario_context.set("hybrid_account_validation_data_key", hybrid_test_data.key)


@when("user opens accounts overview and captures account details from UI")
def user_opens_accounts_overview_and_captures_account_details_from_ui(
    test_context: FrameworkContext,
) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available in scenario context before opening Accounts Overview in hybrid flow.",
    )

    accounts_overview_page = home_page.go_to_accounts_overview()

    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_overview_page_loaded(),
        "Accounts Overview Page",
        "Accounts Overview page is not displayed in hybrid account validation flow.",
        "hybrid_account_validation_accounts_overview_loaded",
    )

    ui_account_ids = accounts_overview_page.get_account_numbers()
    ApiAssertions.assert_list_not_empty(
        ui_account_ids,
        "UI account ids were not captured in hybrid account validation flow.",
    )

    page_source = test_context.page.content()
    customer_id = CustomerUtils.extract_customer_id_from_page_source(page_source)
    cookie_header = CookieUtils.build_cookie_header(test_context.page.context.cookies())

    test_context.customer_id = customer_id
    test_context.cookie_header = cookie_header
    test_context.ui_account_ids = ui_account_ids

    test_context.scenario_context.set("accounts_overview_page", accounts_overview_page)
    test_context.scenario_context.set("ui_account_ids", ui_account_ids)
    test_context.scenario_context.set("customer_id", customer_id)
    test_context.scenario_context.set("cookie_header", cookie_header)


@when("user fetches account details from API for the same customer")
def user_fetches_account_details_from_api_for_the_same_customer(
    test_context: FrameworkContext,
    framework_playwright: Playwright,
    request,
) -> None:
    customer_id = test_context.scenario_context.get("customer_id")
    cookie_header = test_context.scenario_context.get("cookie_header")

    CommonAssertions.assert_not_none(
        customer_id,
        "Customer id should be available before calling the accounts API in hybrid flow.",
    )
    CommonAssertions.assert_not_none(
        cookie_header,
        "Cookie header should be available before calling the accounts API in hybrid flow.",
    )

    service = _get_or_create_accounts_api_service(test_context, framework_playwright, request)
    response = service.get_accounts_response_by_customer_id(int(customer_id), str(cookie_header))

    ApiAssertions.assert_status_code(
        response.status_code,
        200,
        "Accounts API status code mismatch in hybrid account validation flow.",
    )
    ApiAssertions.assert_response_is_list(
        response.json_payload,
        "Accounts API payload should be a list in hybrid account validation flow.",
    )

    api_account_ids: list[str] = []

    for account in response.json_payload:
        if isinstance(account, dict) and account.get("id") is not None:
            api_account_ids.append(str(account.get("id")))

    ApiAssertions.assert_list_not_empty(
        api_account_ids,
        "API account ids were not captured in hybrid account validation flow.",
    )

    test_context.api_account_ids = api_account_ids
    test_context.scenario_context.set("api_status_code", response.status_code)
    test_context.scenario_context.set("api_account_ids", api_account_ids)


@then("API and UI account numbers should match")
def api_and_ui_account_numbers_should_match(
    test_context: FrameworkContext,
) -> None:
    api_status_code = test_context.scenario_context.get("api_status_code")
    ui_account_ids = test_context.scenario_context.get("ui_account_ids")
    api_account_ids = test_context.scenario_context.get("api_account_ids")

    CommonAssertions.assert_not_none(
        api_status_code,
        "API status code should be available in scenario context for hybrid validation.",
    )
    CommonAssertions.assert_not_none(
        ui_account_ids,
        "UI account ids should be available in scenario context for hybrid validation.",
    )
    CommonAssertions.assert_not_none(
        api_account_ids,
        "API account ids should be available in scenario context for hybrid validation.",
    )

    ApiAssertions.assert_status_code(
        int(api_status_code),
        200,
        "Accounts API status code mismatch.",
    )
    ApiAssertions.assert_list_not_empty(
        list(ui_account_ids),
        "UI account ids should not be empty in hybrid validation.",
    )
    ApiAssertions.assert_list_not_empty(
        list(api_account_ids),
        "API account ids should not be empty in hybrid validation.",
    )
    ApiAssertions.assert_collections_match_ignoring_order(
        list(api_account_ids),
        list(ui_account_ids),
        "API and UI account id collections do not match.",
    )