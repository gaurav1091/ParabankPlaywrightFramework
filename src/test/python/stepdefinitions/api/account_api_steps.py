from __future__ import annotations

from pytest_bdd import given, then, when
from playwright.sync_api import Playwright

from com.parabank.automation.api.services.accounts_api_service import AccountsApiService
from com.parabank.automation.assertions.api_assertions import ApiAssertions
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.pages.login_page import LoginPage
from com.parabank.automation.utils.cookie_utils import CookieUtils
from com.parabank.automation.utils.customer_utils import CustomerUtils


@given(
    "authenticated API session is prepared using browser-backed login",
    target_fixture="authenticated_api_context",
)
def authenticated_api_session_is_prepared_using_browser_backed_login(
    framework_page,
    framework_playwright: Playwright,
    framework_config: ConfigManager,
    request,
) -> dict:
    login_page = LoginPage(framework_page, framework_config)
    login_page.open_login_page()

    ApiAssertions.LOGGER.info("Preparing authenticated API session using browser-backed login.")

    if not login_page.is_login_page_displayed():
        raise AssertionError("Login page is not displayed for authenticated API setup.")

    home_page = login_page.login(
        framework_config.get_username(),
        framework_config.get_password(),
    )

    if not home_page.is_home_page_loaded():
        raise AssertionError("Home page is not displayed after API authentication login.")

    accounts_overview_page = home_page.go_to_accounts_overview()

    if not accounts_overview_page.is_accounts_overview_page_loaded():
        raise AssertionError("Accounts Overview page is not displayed during authenticated API setup.")

    page_source = framework_page.content()
    customer_id = CustomerUtils.extract_customer_id_from_page_source(page_source)
    ui_account_ids = accounts_overview_page.get_account_numbers()

    cookies = framework_page.context.cookies()
    cookie_header = CookieUtils.build_cookie_header(cookies)

    service = AccountsApiService(framework_playwright, framework_config)
    request.addfinalizer(service.dispose)

    ApiAssertions.assert_list_not_empty(
        ui_account_ids,
        "UI account ids were not captured during authenticated API setup.",
    )

    return {
        "service": service,
        "customer_id": customer_id,
        "ui_account_ids": ui_account_ids,
        "cookie_header": cookie_header,
    }


@when(
    "user requests account details through API for the authenticated customer",
    target_fixture="authenticated_accounts_api_result",
)
def user_requests_account_details_through_api_for_the_authenticated_customer(
    authenticated_api_context: dict,
) -> dict:
    service: AccountsApiService = authenticated_api_context["service"]
    customer_id: int = authenticated_api_context["customer_id"]
    cookie_header: str = authenticated_api_context["cookie_header"]

    accounts_response = service.get_accounts_response_by_customer_id(customer_id, cookie_header)
    payload = accounts_response.json_payload

    ApiAssertions.assert_response_is_list(
        payload,
        f"Expected accounts payload to be a list for customerId={customer_id}.",
    )

    account_ids_from_payload: list[str] = []

    for account in payload:
        account_id = account.get("id") if isinstance(account, dict) else None
        if account_id is not None:
            account_ids_from_payload.append(str(account_id))

    return {
        "customer_id": customer_id,
        "accounts_response": accounts_response,
        "accounts_payload": payload,
        "account_ids_from_payload": account_ids_from_payload,
    }


@then("accounts API response status should be 200")
def accounts_api_response_status_should_be_200(authenticated_accounts_api_result: dict) -> None:
    accounts_response = authenticated_accounts_api_result["accounts_response"]

    ApiAssertions.assert_status_code(
        accounts_response.status_code,
        200,
        "Accounts API status code mismatch.",
    )


@then("accounts API response should contain at least one account")
def accounts_api_response_should_contain_at_least_one_account(authenticated_accounts_api_result: dict) -> None:
    payload = authenticated_accounts_api_result["accounts_payload"]

    ApiAssertions.assert_list_not_empty(
        payload,
        "Accounts API returned an empty account list.",
    )


@then("each account should contain valid core details")
def each_account_should_contain_valid_core_details(authenticated_accounts_api_result: dict) -> None:
    payload = authenticated_accounts_api_result["accounts_payload"]

    ApiAssertions.assert_json_matches_schema(
        payload,
        "accounts-response-schema.json",
        "Accounts API schema validation failed.",
    )
    ApiAssertions.assert_all_accounts_have_valid_core_fields(
        payload,
        "Accounts API returned one or more invalid account objects.",
    )