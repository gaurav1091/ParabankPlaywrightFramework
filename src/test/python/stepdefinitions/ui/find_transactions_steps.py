from pytest_bdd import then, when, parsers

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.find_transactions_test_data_provider import FindTransactionsTestDataProvider


@when(parsers.parse('the user completes a transfer using find transactions test data key "{test_data_key}"'))
def complete_transfer_using_find_transactions_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before transfer for transaction search.",
    )

    find_transactions_test_data = FindTransactionsTestDataProvider.get_find_transactions_test_data_by_key(test_data_key)
    test_context.scenario_context.set("find_transactions_test_data", find_transactions_test_data)

    transfer_funds_page = home_page.go_to_transfer_funds()

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_funds_page_loaded(),
        "Transfer Funds Page",
        "Transfer Funds page is not displayed.",
        "find_transactions_transfer_page_loaded",
    )

    transfer_funds_page.enter_amount(find_transactions_test_data.amount).select_first_available_accounts()
    transferred_from_account = transfer_funds_page.get_selected_from_account()
    test_context.scenario_context.set("transferred_from_account", transferred_from_account)

    transfer_funds_page.click_transfer_button()

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_successful(),
        "Transfer Complete Confirmation",
        "Transfer was not completed successfully before transaction search.",
        "find_transactions_transfer_success",
    )


@when("the user navigates to the Find Transactions page")
def navigate_to_find_transactions_page(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before navigating to Find Transactions page.",
    )

    find_transactions_page = home_page.go_to_find_transactions()
    test_context.scenario_context.set("find_transactions_page", find_transactions_page)


@then("the Find Transactions page should be displayed")
def verify_find_transactions_page_displayed(test_context: FrameworkContext) -> None:
    find_transactions_page = test_context.scenario_context.get("find_transactions_page")
    CommonAssertions.assert_not_none(
        find_transactions_page,
        "Find Transactions page should be available in scenario context.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        find_transactions_page.is_find_transactions_page_loaded(),
        "Find Transactions Page",
        "Find Transactions page is not displayed.",
        "find_transactions_page_loaded",
    )
    UiAssertions.assert_text_equals(
        test_context.page,
        find_transactions_page.get_page_heading_text(),
        "Find Transactions",
        "Find Transactions page title is incorrect.",
        "find_transactions_page_title",
    )


@when(parsers.parse('the user searches transactions by amount using the same test data key "{test_data_key}"'))
def search_transactions_by_amount_using_same_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    find_transactions_page = test_context.scenario_context.get("find_transactions_page")
    CommonAssertions.assert_not_none(
        find_transactions_page,
        "Find Transactions page should be available before transaction search.",
    )

    find_transactions_test_data = FindTransactionsTestDataProvider.get_find_transactions_test_data_by_key(test_data_key)
    transferred_from_account = test_context.scenario_context.get("transferred_from_account")

    CommonAssertions.assert_not_none(
        transferred_from_account,
        "Transferred source account should be available before transaction search.",
    )

    find_transactions_page = find_transactions_page.find_transactions_by_amount(
        transferred_from_account,
        find_transactions_test_data.amount,
    )
    test_context.scenario_context.set("find_transactions_page", find_transactions_page)
    test_context.scenario_context.set("find_transactions_test_data", find_transactions_test_data)


@then("matching transactions should be displayed")
def verify_matching_transactions_displayed(test_context: FrameworkContext) -> None:
    find_transactions_page = test_context.scenario_context.get("find_transactions_page")
    CommonAssertions.assert_not_none(
        find_transactions_page,
        "Find Transactions page should be available for transaction result validation.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        find_transactions_page.is_transactions_table_visible(),
        "Transactions Table",
        "Transactions table is not displayed.",
        "find_transactions_table_visible",
    )

    CommonAssertions.assert_true(
        find_transactions_page.is_at_least_one_transaction_displayed(),
        "No transaction rows are displayed.",
    )


@then("the displayed transaction amount should match the searched amount")
def verify_displayed_transaction_amount_matches_searched_amount(test_context: FrameworkContext) -> None:
    find_transactions_page = test_context.scenario_context.get("find_transactions_page")
    find_transactions_test_data = test_context.scenario_context.get("find_transactions_test_data")

    CommonAssertions.assert_not_none(
        find_transactions_page,
        "Find Transactions page should be available for amount validation.",
    )
    CommonAssertions.assert_not_none(
        find_transactions_test_data,
        "Find Transactions test data should be available for amount validation.",
    )

    CommonAssertions.assert_true(
        find_transactions_page.is_matching_amount_displayed(find_transactions_test_data.amount),
        "No transaction with the searched amount is displayed.",
    )