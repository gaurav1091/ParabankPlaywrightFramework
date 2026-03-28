from __future__ import annotations

from decimal import Decimal

from pytest_bdd import parsers, then, when

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.find_transactions_test_data_provider import FindTransactionsTestDataProvider
from com.parabank.automation.pages.home_page import HomePage
from stepdefinitions.ui.account_setup_helper import ensure_at_least_two_accounts_for_transfer


def _to_money_decimal(value: str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _search_with_fallback_account(
    test_context: FrameworkContext,
    primary_account: str,
    fallback_account: str,
    amount: str,
) -> tuple[object, str]:
    home_page = HomePage(test_context.page, test_context.config_manager)
    find_transactions_page = home_page.go_to_find_transactions()

    UiAssertions.assert_element_visible(
        test_context.page,
        find_transactions_page.is_find_transactions_page_loaded(),
        "Find Transactions Page",
        "Find Transactions page should be displayed before transaction search.",
        "find_transactions_page_loaded_before_search",
    )

    find_transactions_page = find_transactions_page.find_transactions_by_amount(primary_account, amount)

    if find_transactions_page.is_transactions_table_visible() and find_transactions_page.is_matching_amount_displayed(amount):
        return find_transactions_page, primary_account

    test_context.page.wait_for_timeout(1000)

    home_page = HomePage(test_context.page, test_context.config_manager)
    find_transactions_page = home_page.go_to_find_transactions()
    find_transactions_page = find_transactions_page.find_transactions_by_amount(fallback_account, amount)

    return find_transactions_page, fallback_account


@when(parsers.parse('the user completes a transfer using find transactions test data key "{test_data_key}"'))
def complete_transfer_using_find_transactions_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before transfer for transaction search.",
    )

    find_transactions_test_data = FindTransactionsTestDataProvider.get_find_transactions_test_data_by_key(test_data_key)
    test_context.scenario_context.set("find_transactions_test_data", find_transactions_test_data)

    ensure_at_least_two_accounts_for_transfer(test_context)

    home_page = HomePage(test_context.page, test_context.config_manager)
    transfer_funds_page = home_page.go_to_transfer_funds()

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_funds_page_loaded(),
        "Transfer Funds Page",
        "Transfer Funds page is not displayed before creating transaction for search.",
        "find_transactions_transfer_page_loaded",
    )

    transfer_funds_page.enter_amount(find_transactions_test_data.amount).select_first_available_accounts()

    transferred_from_account = transfer_funds_page.get_selected_from_account()
    transferred_to_account = transfer_funds_page.get_selected_to_account()

    CommonAssertions.assert_not_none(
        transferred_from_account,
        "Transferred source account should be selected before transaction search transfer.",
    )
    CommonAssertions.assert_not_none(
        transferred_to_account,
        "Transferred destination account should be selected before transaction search transfer.",
    )
    CommonAssertions.assert_true(
        str(transferred_from_account).strip() != str(transferred_to_account).strip(),
        "Transferred source and destination accounts should be different for Find Transactions setup.",
    )

    transfer_funds_page = transfer_funds_page.click_transfer_button()

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_successful(),
        "Transfer Complete Confirmation",
        "Transfer was not completed successfully before transaction search.",
        "find_transactions_transfer_success",
    )

    test_context.scenario_context.set("transferred_from_account", transferred_from_account)
    test_context.scenario_context.set("transferred_to_account", transferred_to_account)
    test_context.scenario_context.set("submitted_find_transactions_amount_text", find_transactions_test_data.amount)
    test_context.scenario_context.set("transfer_funds_page", transfer_funds_page)


@when("the user navigates to the Find Transactions page")
def navigate_to_find_transactions_page(test_context: FrameworkContext) -> None:
    home_page = HomePage(test_context.page, test_context.config_manager)
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
    transferred_from_account = test_context.scenario_context.get("transferred_from_account")
    transferred_to_account = test_context.scenario_context.get("transferred_to_account")
    find_transactions_test_data = test_context.scenario_context.get("find_transactions_test_data")

    CommonAssertions.assert_not_none(
        transferred_from_account,
        "Transferred source account should be available before transaction search.",
    )
    CommonAssertions.assert_not_none(
        transferred_to_account,
        "Transferred destination account should be available before transaction search.",
    )
    CommonAssertions.assert_not_none(
        find_transactions_test_data,
        "Find Transactions test data should be available before transaction search.",
    )

    find_transactions_page, searched_account = _search_with_fallback_account(
        test_context=test_context,
        primary_account=str(transferred_from_account),
        fallback_account=str(transferred_to_account),
        amount=find_transactions_test_data.amount,
    )

    test_context.scenario_context.set("find_transactions_page", find_transactions_page)
    test_context.scenario_context.set("searched_transactions_account", searched_account)


@then("matching transactions should be displayed")
def verify_matching_transactions_displayed(test_context: FrameworkContext) -> None:
    find_transactions_page = test_context.scenario_context.get("find_transactions_page")
    find_transactions_test_data = test_context.scenario_context.get("find_transactions_test_data")
    searched_transactions_account = test_context.scenario_context.get("searched_transactions_account")

    CommonAssertions.assert_not_none(
        find_transactions_page,
        "Find Transactions page should be available for transaction result validation.",
    )
    CommonAssertions.assert_not_none(
        find_transactions_test_data,
        "Find Transactions test data should be available for transaction result validation.",
    )

    CommonAssertions.assert_true(
        find_transactions_page.is_transactions_table_visible(),
        "Transactions table is not displayed after searching transferred amount. "
        f"Searched account={searched_transactions_account} | "
        f"No-results message='{find_transactions_page.get_no_transactions_message_text()}'",
    )

    CommonAssertions.assert_true(
        find_transactions_page.is_at_least_one_transaction_displayed(),
        "No transaction rows are displayed.",
    )
    CommonAssertions.assert_true(
        find_transactions_page.is_matching_amount_displayed(find_transactions_test_data.amount),
        "No transaction with the searched amount is displayed.",
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
        find_transactions_page.are_all_displayed_transaction_amounts_matching(find_transactions_test_data.amount),
        "Displayed transaction amounts do not all match the searched amount.",
    )


@then("the search results should be correct for the searched account and amount")
def verify_search_results_correct_for_searched_account_and_amount(test_context: FrameworkContext) -> None:
    find_transactions_page = test_context.scenario_context.get("find_transactions_page")
    find_transactions_test_data = test_context.scenario_context.get("find_transactions_test_data")

    CommonAssertions.assert_not_none(
        find_transactions_page,
        "Find Transactions page should be available for correctness validation.",
    )
    CommonAssertions.assert_not_none(
        find_transactions_test_data,
        "Find Transactions test data should be available for correctness validation.",
    )

    CommonAssertions.assert_true(
        find_transactions_page.is_transaction_search_result_correct(find_transactions_test_data.amount),
        "Find Transactions search results are not correct for the searched amount.",
    )