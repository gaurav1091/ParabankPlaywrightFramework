from pytest_bdd import then, when, parsers

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.open_new_account_test_data_provider import OpenNewAccountTestDataProvider


MINIMUM_SOURCE_ACCOUNT_BALANCE_FOR_NEW_ACCOUNT = 10


@when("the user navigates to the Open New Account page")
def navigate_to_open_new_account_page(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before navigating to Open New Account page.",
    )

    open_new_account_page = home_page.go_to_open_new_account()
    test_context.scenario_context.set("open_new_account_page", open_new_account_page)


@then("the Open New Account page should be displayed")
def verify_open_new_account_page_displayed(test_context: FrameworkContext) -> None:
    open_new_account_page = test_context.scenario_context.get("open_new_account_page")
    CommonAssertions.assert_not_none(
        open_new_account_page,
        "Open New Account page should be available in scenario context.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        open_new_account_page.is_open_new_account_page_loaded(),
        "Open New Account Page",
        "Open New Account page is not displayed.",
        "open_new_account_page_loaded",
    )
    UiAssertions.assert_text_equals(
        test_context.page,
        open_new_account_page.get_page_heading_text(),
        "Open New Account",
        "Open New Account page title is incorrect.",
        "open_new_account_title",
    )


@when(parsers.parse('the user creates a new account using test data key "{test_data_key}"'))
def create_new_account_using_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    open_new_account_page = test_context.scenario_context.get("open_new_account_page")
    CommonAssertions.assert_not_none(
        open_new_account_page,
        "Open New Account page should be available before account creation.",
    )

    open_new_account_test_data = OpenNewAccountTestDataProvider.get_open_new_account_test_data_by_key(test_data_key)
    test_context.scenario_context.set("open_new_account_test_data", open_new_account_test_data)

    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before selecting a source account for new account creation.",
    )

    accounts_overview_page = home_page.go_to_accounts_overview()
    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_overview_page_loaded(),
        "Accounts Overview Page",
        "Accounts Overview page should be displayed before determining source accounts.",
        "open_new_account_accounts_overview_loaded",
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
        "New account could not be confirmed using any eligible source account. "
        f"Attempts={attempt_summaries}",
    )
    CommonAssertions.assert_not_none(
        created_account_number,
        "Open New Account flow did not produce a detectable new account number in Accounts Overview. "
        f"Attempts={attempt_summaries}",
    )


@then("the new account should be created successfully")
def verify_new_account_created_successfully(test_context: FrameworkContext) -> None:
    created_account_number = test_context.scenario_context.get("created_account_number")
    successful_source_account = test_context.scenario_context.get("successful_source_account")

    CommonAssertions.assert_not_none(
        successful_source_account,
        "Source account used for successful new account creation should be available.",
    )
    CommonAssertions.assert_not_none(
        created_account_number,
        "Created account number should be available after successful new account creation.",
    )

    CommonAssertions.assert_true(
        str(created_account_number).isdigit(),
        "Created account number should be numeric.",
    )


@then("the new account number should be displayed")
def verify_new_account_number_displayed(test_context: FrameworkContext) -> None:
    created_account_number = test_context.scenario_context.get("created_account_number")

    CommonAssertions.assert_not_none(
        created_account_number,
        "Created account number should be available in scenario context.",
    )
    CommonAssertions.assert_true(
        str(created_account_number).isdigit(),
        "New account number should be numeric.",
    )

    test_context.scenario_context.set("new_account_number", str(created_account_number))