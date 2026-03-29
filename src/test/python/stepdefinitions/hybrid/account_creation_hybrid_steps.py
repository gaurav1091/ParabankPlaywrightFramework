from __future__ import annotations

from playwright.sync_api import Playwright
from pytest_bdd import given, parsers, then, when

from com.parabank.automation.api.services.accounts_api_service import AccountsApiService
from com.parabank.automation.assertions.api_assertions import ApiAssertions
from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.hybrid_ui_to_api_account_creation_test_data_provider import (
    HybridUiToApiAccountCreationTestDataProvider,
)
from com.parabank.automation.dataproviders.login_test_data_provider import LoginTestDataProvider
from com.parabank.automation.dataproviders.open_new_account_test_data_provider import (
    OpenNewAccountTestDataProvider,
)
from com.parabank.automation.pages.home_page import HomePage
from com.parabank.automation.pages.login_page import LoginPage
from com.parabank.automation.utils.cookie_utils import CookieUtils
from com.parabank.automation.utils.customer_utils import CustomerUtils

HYBRID_ACCOUNTS_API_SERVICE_CONTEXT_KEY = "hybrid_accounts_api_service_for_creation_flow"
MINIMUM_SOURCE_ACCOUNT_BALANCE_FOR_NEW_ACCOUNT = 10


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


def _extract_account_ids_from_accounts_response_payload(payload: list[dict]) -> list[str]:
    account_ids: list[str] = []

    for account in payload:
        if isinstance(account, dict) and account.get("id") is not None:
            account_ids.append(str(account.get("id")))

    return account_ids


@given(parsers.parse('user logs in for hybrid account creation using key "{test_data_key}"'))
def user_logs_in_for_hybrid_account_creation_using_key(
    test_context: FrameworkContext,
    test_data_key: str,
) -> None:
    test_context.scenario_context.clear()
    test_context.reset_hybrid_state()

    hybrid_test_data = HybridUiToApiAccountCreationTestDataProvider.get_by_key(test_data_key)
    login_test_data = LoginTestDataProvider.get_login_test_data_by_key(hybrid_test_data.login_key)

    login_page = LoginPage(test_context.page, test_context.config_manager)
    login_page.open_login_page()

    UiAssertions.assert_element_visible(
        test_context.page,
        login_page.is_login_page_displayed(),
        "Login Page",
        "Login page is not displayed for hybrid account creation flow.",
        "hybrid_account_creation_login_page_displayed",
    )

    home_page = login_page.login(
        login_test_data.username,
        login_test_data.password,
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        home_page.is_home_page_loaded(),
        "Home Page",
        "Home page is not displayed after hybrid account creation login.",
        "hybrid_account_creation_home_page_loaded",
    )

    test_context.scenario_context.set("home_page", home_page)
    test_context.scenario_context.set("hybrid_account_creation_data_key", hybrid_test_data.key)


@when("user captures current account details from UI and API before account creation")
def user_captures_current_account_details_from_ui_and_api_before_account_creation(
    test_context: FrameworkContext,
    framework_playwright: Playwright,
    request,
) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before capturing pre-account-creation details.",
    )

    accounts_overview_page = home_page.go_to_accounts_overview()

    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_overview_page_loaded(),
        "Accounts Overview Page",
        "Accounts Overview page is not displayed before hybrid account creation.",
        "hybrid_account_creation_accounts_overview_pre_loaded",
    )

    pre_ui_account_ids = accounts_overview_page.get_account_numbers()
    ApiAssertions.assert_list_not_empty(
        pre_ui_account_ids,
        "UI account ids before account creation should not be empty.",
    )

    page_source = test_context.page.content()
    customer_id = CustomerUtils.extract_customer_id_from_page_source(page_source)
    cookie_header = CookieUtils.build_cookie_header(test_context.page.context.cookies())

    service = _get_or_create_accounts_api_service(test_context, framework_playwright, request)
    response = service.get_accounts_response_by_customer_id(customer_id, cookie_header)

    ApiAssertions.assert_status_code(
        response.status_code,
        200,
        "Accounts API status code before account creation is incorrect.",
    )
    ApiAssertions.assert_response_is_list(
        response.json_payload,
        "Accounts API payload before account creation should be a list.",
    )

    pre_api_account_ids = _extract_account_ids_from_accounts_response_payload(response.json_payload)

    ApiAssertions.assert_list_not_empty(
        pre_api_account_ids,
        "API account ids before account creation should not be empty.",
    )

    test_context.customer_id = customer_id
    test_context.cookie_header = cookie_header

    test_context.scenario_context.set("customer_id", customer_id)
    test_context.scenario_context.set("cookie_header", cookie_header)
    test_context.scenario_context.set("pre_ui_account_ids", pre_ui_account_ids)
    test_context.scenario_context.set("pre_api_account_ids", pre_api_account_ids)


@when(parsers.parse('user creates a new account in UI using hybrid account creation key "{test_data_key}"'))
def user_creates_a_new_account_in_ui_using_hybrid_account_creation_key(
    test_context: FrameworkContext,
    test_data_key: str,
) -> None:
    hybrid_test_data = HybridUiToApiAccountCreationTestDataProvider.get_by_key(test_data_key)
    open_new_account_test_data = OpenNewAccountTestDataProvider.get_open_new_account_test_data_by_key(
        hybrid_test_data.open_new_account_key
    )

    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before opening the Open New Account page in hybrid flow.",
    )

    accounts_overview_page = home_page.go_to_accounts_overview()
    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_overview_page_loaded(),
        "Accounts Overview Page",
        "Accounts Overview page should be displayed before determining source accounts.",
        "hybrid_account_creation_accounts_overview_loaded",
    )

    baseline_account_numbers = accounts_overview_page.get_account_numbers()
    test_context.scenario_context.set("baseline_account_numbers_before_open_new_account", baseline_account_numbers)

    candidate_accounts = accounts_overview_page.get_eligible_source_accounts_for_new_account(
        MINIMUM_SOURCE_ACCOUNT_BALANCE_FOR_NEW_ACCOUNT
    )
    test_context.scenario_context.set("open_new_account_candidate_accounts", candidate_accounts)

    successful_source_account: str | None = None
    created_account_number: str | None = None
    attempt_summaries: list[str] = []

    for candidate_account in candidate_accounts:
        open_new_account_page = home_page.go_to_open_new_account()
        available_from_accounts = open_new_account_page.get_available_from_accounts()

        if candidate_account not in available_from_accounts:
            attempt_summaries.append(f"{candidate_account}=not_present_in_dropdown")
            continue

        open_new_account_page = open_new_account_page.open_new_account_from_specific_source(
            open_new_account_test_data.account_type,
            candidate_account,
        )

        visible_ui_success = open_new_account_page.is_account_creation_successful()
        feedback_message = open_new_account_page.get_submission_feedback_message()

        accounts_overview_page_after_submit = home_page.go_to_accounts_overview()
        current_account_numbers = accounts_overview_page_after_submit.get_account_numbers()
        new_accounts = accounts_overview_page_after_submit.get_new_account_numbers_since(baseline_account_numbers)

        if new_accounts:
            created_account_number = new_accounts[-1]
            successful_source_account = candidate_account
            attempt_summaries.append(
                f"{candidate_account}=SUCCESS(created_account={created_account_number}, "
                f"ui_success={visible_ui_success}, feedback={feedback_message})"
            )

            test_context.scenario_context.set("created_account_number", created_account_number)
            test_context.scenario_context.set("successful_source_account", candidate_account)
            test_context.scenario_context.set("accounts_after_open_new_account", current_account_numbers)
            test_context.scenario_context.set("open_new_account_feedback_message", feedback_message)

            open_new_account_page = home_page.go_to_open_new_account()
            test_context.scenario_context.set("open_new_account_page", open_new_account_page)
            break

        attempt_summaries.append(
            f"{candidate_account}=NO_NEW_ACCOUNT(ui_success={visible_ui_success}, feedback={feedback_message})"
        )

    test_context.scenario_context.set("open_new_account_attempt_summaries", attempt_summaries)

    CommonAssertions.assert_not_none(
        successful_source_account,
        "New account could not be confirmed using any eligible source account in hybrid flow. "
        f"Attempts={attempt_summaries}",
    )
    CommonAssertions.assert_not_none(
        created_account_number,
        "Open New Account flow did not produce a detectable new account number in Accounts Overview "
        f"during hybrid flow. Attempts={attempt_summaries}",
    )


@when("user refreshes account details from UI and API after account creation")
def user_refreshes_account_details_from_ui_and_api_after_account_creation(
    test_context: FrameworkContext,
    framework_playwright: Playwright,
    request,
) -> None:
    customer_id = test_context.scenario_context.get("customer_id")
    cookie_header = test_context.scenario_context.get("cookie_header")

    CommonAssertions.assert_not_none(
        customer_id,
        "Customer id should be available before refreshing post-account-creation details.",
    )
    CommonAssertions.assert_not_none(
        cookie_header,
        "Cookie header should be available before refreshing post-account-creation details.",
    )

    home_page = HomePage(test_context.page, test_context.config_manager)
    accounts_overview_page = home_page.go_to_accounts_overview()

    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_overview_page_loaded(),
        "Accounts Overview Page",
        "Accounts Overview page is not displayed after hybrid account creation.",
        "hybrid_account_creation_accounts_overview_post_loaded",
    )

    post_ui_account_ids = accounts_overview_page.get_account_numbers()
    ApiAssertions.assert_list_not_empty(
        post_ui_account_ids,
        "UI account ids after account creation should not be empty.",
    )

    service = _get_or_create_accounts_api_service(test_context, framework_playwright, request)
    response = service.get_accounts_response_by_customer_id(int(customer_id), str(cookie_header))

    ApiAssertions.assert_status_code(
        response.status_code,
        200,
        "Accounts API status code after account creation is incorrect.",
    )
    ApiAssertions.assert_response_is_list(
        response.json_payload,
        "Accounts API payload after account creation should be a list.",
    )

    post_api_account_ids = _extract_account_ids_from_accounts_response_payload(response.json_payload)

    ApiAssertions.assert_list_not_empty(
        post_api_account_ids,
        "API account ids after account creation should not be empty.",
    )

    test_context.scenario_context.set("post_ui_account_ids", post_ui_account_ids)
    test_context.scenario_context.set("post_api_account_ids", post_api_account_ids)


@then("the new account should be present in both UI and API account lists")
def the_new_account_should_be_present_in_both_ui_and_api_account_lists(
    test_context: FrameworkContext,
) -> None:
    new_account_id = test_context.scenario_context.get("created_account_number")
    post_ui_account_ids = test_context.scenario_context.get("post_ui_account_ids")
    post_api_account_ids = test_context.scenario_context.get("post_api_account_ids")

    CommonAssertions.assert_not_none(
        new_account_id,
        "New account id is not available in scenario context.",
    )
    CommonAssertions.assert_not_none(
        post_ui_account_ids,
        "Post-account-creation UI account ids are not available in scenario context.",
    )
    CommonAssertions.assert_not_none(
        post_api_account_ids,
        "Post-account-creation API account ids are not available in scenario context.",
    )

    CommonAssertions.assert_contains(
        list(post_ui_account_ids),
        str(new_account_id),
        "New account id is not present in UI account list after account creation.",
    )
    CommonAssertions.assert_contains(
        list(post_api_account_ids),
        str(new_account_id),
        "New account id is not present in API account list after account creation.",
    )


@then("account count should increase by one in both UI and API")
def account_count_should_increase_by_one_in_both_ui_and_api(
    test_context: FrameworkContext,
) -> None:
    pre_ui_account_ids = test_context.scenario_context.get("pre_ui_account_ids")
    post_ui_account_ids = test_context.scenario_context.get("post_ui_account_ids")
    pre_api_account_ids = test_context.scenario_context.get("pre_api_account_ids")
    post_api_account_ids = test_context.scenario_context.get("post_api_account_ids")

    CommonAssertions.assert_not_none(
        pre_ui_account_ids,
        "Pre-account-creation UI account ids should be available in scenario context.",
    )
    CommonAssertions.assert_not_none(
        post_ui_account_ids,
        "Post-account-creation UI account ids should be available in scenario context.",
    )
    CommonAssertions.assert_not_none(
        pre_api_account_ids,
        "Pre-account-creation API account ids should be available in scenario context.",
    )
    CommonAssertions.assert_not_none(
        post_api_account_ids,
        "Post-account-creation API account ids should be available in scenario context.",
    )

    CommonAssertions.assert_equals(
        len(list(post_ui_account_ids)),
        len(list(pre_ui_account_ids)) + 1,
        "UI account count did not increase by exactly one after account creation.",
    )
    CommonAssertions.assert_equals(
        len(list(post_api_account_ids)),
        len(list(pre_api_account_ids)) + 1,
        "API account count did not increase by exactly one after account creation.",
    )
