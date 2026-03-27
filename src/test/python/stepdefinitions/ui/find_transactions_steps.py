from __future__ import annotations

import time
from decimal import Decimal

from pytest_bdd import then, when, parsers

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.find_transactions_test_data_provider import FindTransactionsTestDataProvider


def _to_money_decimal(value: str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _generate_unique_find_transactions_amount(base_amount: str) -> Decimal:
    base_decimal = _to_money_decimal(base_amount)
    cents_component = (int(time.time() * 1000) % 90) + 10
    unique_amount = (base_decimal + (Decimal(cents_component) / Decimal("100"))).quantize(Decimal("0.01"))
    return unique_amount


def _to_money_text(value: Decimal) -> str:
    return f"{value:.2f}"


@when(parsers.parse('the user completes a transfer using find transactions test data key "{test_data_key}"'))
def complete_transfer_using_find_transactions_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before transfer for transaction search.",
    )

    find_transactions_test_data = FindTransactionsTestDataProvider.get_find_transactions_test_data_by_key(test_data_key)
    test_context.scenario_context.set("find_transactions_test_data", find_transactions_test_data)

    submitted_amount_decimal = _generate_unique_find_transactions_amount(find_transactions_test_data.amount)
    submitted_amount_text = _to_money_text(submitted_amount_decimal)

    accounts_overview_page = home_page.go_to_accounts_overview()

    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_overview_page_loaded(),
        "Accounts Overview Page",
        "Accounts Overview page should be displayed before selecting transfer candidate accounts for Find Transactions.",
        "find_transactions_accounts_overview_loaded",
    )

    transferred_from_account, transferred_to_account = accounts_overview_page.get_transfer_candidate_accounts(
        submitted_amount_text
    )

    transfer_funds_page = home_page.go_to_transfer_funds()

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_funds_page_loaded(),
        "Transfer Funds Page",
        "Transfer Funds page is not displayed before creating transaction for search.",
        "find_transactions_transfer_page_loaded",
    )

    transfer_funds_page = transfer_funds_page.transfer_funds_between_accounts(
        amount=submitted_amount_text,
        from_account=transferred_from_account,
        to_account=transferred_to_account,
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_successful(),
        "Transfer Complete Confirmation",
        "Transfer was not completed successfully before transaction search.",
        "find_transactions_transfer_success",
    )

    test_context.scenario_context.set("transferred_from_account", transferred_from_account)
    test_context.scenario_context.set("transferred_to_account", transferred_to_account)
    test_context.scenario_context.set("submitted_find_transactions_amount_text", submitted_amount_text)
    test_context.scenario_context.set("transfer_funds_page", transfer_funds_page)


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

    transferred_from_account = test_context.scenario_context.get("transferred_from_account")
    submitted_amount_text = test_context.scenario_context.get("submitted_find_transactions_amount_text")

    CommonAssertions.assert_not_none(
        transferred_from_account,
        "Transferred source account should be available before transaction search.",
    )
    CommonAssertions.assert_not_none(
        submitted_amount_text,
        "Submitted transfer amount should be available before transaction search.",
    )

    find_transactions_page = find_transactions_page.find_transactions_by_amount(
        transferred_from_account,
        submitted_amount_text,
    )
    test_context.scenario_context.set("find_transactions_page", find_transactions_page)


@then("matching transactions should be displayed")
def verify_matching_transactions_displayed(test_context: FrameworkContext) -> None:
    find_transactions_page = test_context.scenario_context.get("find_transactions_page")
    submitted_amount_text = test_context.scenario_context.get("submitted_find_transactions_amount_text")

    CommonAssertions.assert_not_none(
        find_transactions_page,
        "Find Transactions page should be available for transaction result validation.",
    )
    CommonAssertions.assert_not_none(
        submitted_amount_text,
        "Submitted amount should be available for transaction result validation.",
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
    CommonAssertions.assert_true(
        find_transactions_page.is_matching_amount_displayed(submitted_amount_text),
        "No transaction with the searched amount is displayed.",
    )


@then("the displayed transaction amount should match the searched amount")
def verify_displayed_transaction_amount_matches_searched_amount(test_context: FrameworkContext) -> None:
    find_transactions_page = test_context.scenario_context.get("find_transactions_page")
    submitted_amount_text = test_context.scenario_context.get("submitted_find_transactions_amount_text")

    CommonAssertions.assert_not_none(
        find_transactions_page,
        "Find Transactions page should be available for amount validation.",
    )
    CommonAssertions.assert_not_none(
        submitted_amount_text,
        "Submitted amount should be available for amount validation.",
    )

    CommonAssertions.assert_true(
        find_transactions_page.are_all_displayed_transaction_amounts_matching(submitted_amount_text),
        "Displayed transaction amounts do not all match the searched amount.",
    )


@then("the search results should be correct for the searched account and amount")
def verify_search_results_correct_for_searched_account_and_amount(test_context: FrameworkContext) -> None:
    find_transactions_page = test_context.scenario_context.get("find_transactions_page")
    transferred_from_account = test_context.scenario_context.get("transferred_from_account")
    submitted_amount_text = test_context.scenario_context.get("submitted_find_transactions_amount_text")

    CommonAssertions.assert_not_none(
        find_transactions_page,
        "Find Transactions page should be available for correctness validation.",
    )
    CommonAssertions.assert_not_none(
        transferred_from_account,
        "Transferred source account should be available for correctness validation.",
    )
    CommonAssertions.assert_not_none(
        submitted_amount_text,
        "Submitted amount should be available for correctness validation.",
    )

    CommonAssertions.assert_true(
        find_transactions_page.is_transaction_search_result_correct(submitted_amount_text),
        "Find Transactions search results are not correct for the searched account and amount.",
    )