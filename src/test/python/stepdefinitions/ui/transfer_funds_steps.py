from __future__ import annotations

import time
from decimal import Decimal

from pytest_bdd import parsers, then, when

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.transfer_funds_test_data_provider import (
    TransferFundsTestDataProvider,
)
from com.parabank.automation.pages.home_page import HomePage
from stepdefinitions.ui.account_setup_helper import ensure_at_least_two_accounts_for_transfer


def _to_money_decimal(value: str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _to_money_text(value: str) -> str:
    return f"${_to_money_decimal(value):.2f}"


def _normalize_decimal(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _get_account_summary_snapshot(
    accounts_overview_page,
    account_number: str,
) -> tuple[Decimal, Decimal]:
    account_summary = accounts_overview_page.get_account_summary_by_number(str(account_number))

    CommonAssertions.assert_not_none(
        account_summary,
        f"Account summary should exist for account number '{account_number}'.",
    )

    balance_value = account_summary.get("balance")
    available_balance_value = account_summary.get("available_balance")

    CommonAssertions.assert_not_none(
        balance_value,
        f"Balance value should exist for account number '{account_number}'.",
    )
    CommonAssertions.assert_not_none(
        available_balance_value,
        f"Available balance value should exist for account number '{account_number}'.",
    )

    return _normalize_decimal(balance_value), _normalize_decimal(available_balance_value)


def _wait_for_destination_balance_update(
    test_context: FrameworkContext,
    destination_account: str,
    expected_balance: Decimal,
    timeout_seconds: int = 25,
    poll_interval_seconds: int = 2,
) -> Decimal:
    start_time = time.time()
    last_seen_value: Decimal | None = None

    while time.time() - start_time < timeout_seconds:
        home_page = HomePage(test_context.page, test_context.config_manager)
        accounts_overview_page = home_page.go_to_accounts_overview()

        UiAssertions.assert_element_visible(
            test_context.page,
            accounts_overview_page.is_accounts_overview_page_loaded(),
            "Accounts Overview Page",
            "Accounts Overview page should be visible during destination balance polling.",
            "transfer_funds_polling_accounts_overview",
        )

        destination_balance_after, _ = _get_account_summary_snapshot(
            accounts_overview_page,
            str(destination_account),
        )
        last_seen_value = destination_balance_after

        if destination_balance_after == expected_balance:
            return destination_balance_after

        time.sleep(poll_interval_seconds)

    raise AssertionError(
        "Destination balance did not update within timeout. "
        f"Expected={expected_balance!r} | LastSeen={last_seen_value!r} | TimeoutSeconds={timeout_seconds}"
    )


@when("the user navigates to the Transfer Funds page")
def navigate_to_transfer_funds_page(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before navigating to Transfer Funds page.",
    )

    ensure_at_least_two_accounts_for_transfer(test_context)

    home_page = HomePage(test_context.page, test_context.config_manager)
    transfer_funds_page = home_page.go_to_transfer_funds()
    test_context.scenario_context.set("transfer_funds_page", transfer_funds_page)


@then("the Transfer Funds page should be displayed")
def verify_transfer_funds_page_displayed(test_context: FrameworkContext) -> None:
    transfer_funds_page = test_context.scenario_context.get("transfer_funds_page")
    CommonAssertions.assert_not_none(
        transfer_funds_page,
        "Transfer Funds page should be available in scenario context.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_funds_page_loaded(),
        "Transfer Funds Page",
        "Transfer Funds page is not displayed.",
        "transfer_funds_page_loaded",
    )

    UiAssertions.assert_text_equals(
        test_context.page,
        transfer_funds_page.get_page_heading_text(),
        "Transfer Funds",
        "Transfer Funds page title is incorrect.",
        "transfer_funds_page_title",
    )


@when(parsers.parse('the user transfers funds using test data key "{test_data_key}"'))
def transfer_funds_using_test_data_key(
    test_context: FrameworkContext,
    test_data_key: str,
) -> None:
    transfer_funds_test_data = TransferFundsTestDataProvider.get_transfer_funds_test_data_by_key(test_data_key)
    test_context.scenario_context.set("transfer_funds_test_data", transfer_funds_test_data)

    transfer_amount_text = transfer_funds_test_data.amount
    transfer_amount_decimal = _to_money_decimal(transfer_amount_text)

    ensure_at_least_two_accounts_for_transfer(test_context)

    home_page = HomePage(test_context.page, test_context.config_manager)
    transfer_funds_page = home_page.go_to_transfer_funds()

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_funds_page_loaded(),
        "Transfer Funds Page",
        "Transfer Funds page should be displayed before transfer execution.",
        "transfer_funds_page_loaded_before_execution",
    )

    available_from_accounts = transfer_funds_page.get_available_from_accounts()
    available_to_accounts = transfer_funds_page.get_available_to_accounts()

    home_page = HomePage(test_context.page, test_context.config_manager)
    accounts_overview_page = home_page.go_to_accounts_overview()

    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_overview_page_loaded(),
        "Accounts Overview Page",
        "Accounts Overview page should be displayed before transfer balance capture.",
        "transfer_funds_accounts_overview_loaded",
    )

    source_account, destination_account = accounts_overview_page.get_transfer_candidate_accounts_from_dropdown_options(
        available_from_accounts,
        available_to_accounts,
        transfer_amount_text,
    )

    CommonAssertions.assert_not_none(
        source_account,
        "A source account should be selected on the Transfer Funds page.",
    )
    CommonAssertions.assert_not_none(
        destination_account,
        "A destination account should be selected on the Transfer Funds page.",
    )
    CommonAssertions.assert_true(
        str(source_account).strip() != str(destination_account).strip(),
        "Transfer source and destination accounts should be different.",
    )

    source_balance_before, source_available_balance_before = _get_account_summary_snapshot(
        accounts_overview_page,
        str(source_account),
    )
    destination_balance_before, destination_available_balance_before = _get_account_summary_snapshot(
        accounts_overview_page,
        str(destination_account),
    )

    CommonAssertions.assert_true(
        source_available_balance_before >= transfer_amount_decimal,
        (
            f"Selected source account '{source_account}' does not have enough available balance "
            f"for transfer amount {transfer_amount_decimal}. "
            f"Available balance: {source_available_balance_before}"
        ),
    )

    test_context.scenario_context.set("transfer_source_account", str(source_account))
    test_context.scenario_context.set("transfer_destination_account", str(destination_account))
    test_context.scenario_context.set("transfer_amount_decimal", transfer_amount_decimal)

    test_context.scenario_context.set("source_balance_before_transfer", source_balance_before)
    test_context.scenario_context.set(
        "source_available_balance_before_transfer",
        source_available_balance_before,
    )

    test_context.scenario_context.set(
        "destination_balance_before_transfer",
        destination_balance_before,
    )
    test_context.scenario_context.set(
        "destination_available_balance_before_transfer",
        destination_available_balance_before,
    )

    home_page = HomePage(test_context.page, test_context.config_manager)
    transfer_funds_page = home_page.go_to_transfer_funds()

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_funds_page_loaded(),
        "Transfer Funds Page",
        "Transfer Funds page should be displayed before explicit transfer execution.",
        "transfer_funds_page_loaded_before_explicit_execution",
    )

    transfer_funds_page = transfer_funds_page.transfer_funds_between_accounts(
        transfer_amount_text,
        str(source_account),
        str(destination_account),
    )

    test_context.scenario_context.set("transfer_funds_page", transfer_funds_page)


@then("the transfer should be completed successfully")
def verify_transfer_completed_successfully(test_context: FrameworkContext) -> None:
    transfer_funds_page = test_context.scenario_context.get("transfer_funds_page")
    CommonAssertions.assert_not_none(
        transfer_funds_page,
        "Transfer Funds page should be available for success validation.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        transfer_funds_page.is_transfer_successful(),
        "Transfer Complete Confirmation",
        "Transfer was not completed successfully.",
        "transfer_funds_success",
    )

    heading_text = transfer_funds_page.get_transfer_complete_heading_text()
    CommonAssertions.assert_true(
        "Transfer Complete" in heading_text,
        f"Transfer completion heading is incorrect. Actual heading: {heading_text}",
    )

    transfer_result_message = transfer_funds_page.get_transfer_result_message()
    if transfer_result_message:
        CommonAssertions.assert_contains(
            transfer_result_message,
            "has been transferred",
            "Transfer success message is incorrect.",
        )


@then("the transferred amount should be displayed correctly")
def verify_transferred_amount_displayed_correctly(test_context: FrameworkContext) -> None:
    transfer_funds_page = test_context.scenario_context.get("transfer_funds_page")
    transfer_funds_test_data = test_context.scenario_context.get("transfer_funds_test_data")

    CommonAssertions.assert_not_none(
        transfer_funds_page,
        "Transfer Funds page should be available for amount validation.",
    )
    CommonAssertions.assert_not_none(
        transfer_funds_test_data,
        "Transfer Funds test data should be available for amount validation.",
    )

    expected_amount = _to_money_text(transfer_funds_test_data.amount)
    actual_amount = transfer_funds_page.get_transferred_amount_value().strip()

    CommonAssertions.assert_equals(
        actual_amount,
        expected_amount,
        "Transferred amount is incorrect.",
    )


@then("the source and destination balances should be updated correctly")
def verify_source_and_destination_balances_updated_correctly(
    test_context: FrameworkContext,
) -> None:
    source_account = test_context.scenario_context.get("transfer_source_account")
    destination_account = test_context.scenario_context.get("transfer_destination_account")
    transfer_amount_decimal = test_context.scenario_context.get("transfer_amount_decimal")

    source_balance_before = test_context.scenario_context.get("source_balance_before_transfer")
    source_available_balance_before = test_context.scenario_context.get("source_available_balance_before_transfer")

    destination_balance_before = test_context.scenario_context.get("destination_balance_before_transfer")
    destination_available_balance_before = test_context.scenario_context.get(
        "destination_available_balance_before_transfer"
    )

    CommonAssertions.assert_not_none(
        source_account,
        "Source account should be present for balance validation.",
    )
    CommonAssertions.assert_not_none(
        destination_account,
        "Destination account should be present for balance validation.",
    )
    CommonAssertions.assert_not_none(
        transfer_amount_decimal,
        "Transfer amount should be present for balance validation.",
    )

    CommonAssertions.assert_not_none(
        source_balance_before,
        "Source pre-transfer balance should be present.",
    )
    CommonAssertions.assert_not_none(
        source_available_balance_before,
        "Source pre-transfer available balance should be present.",
    )
    CommonAssertions.assert_not_none(
        destination_balance_before,
        "Destination pre-transfer balance should be present.",
    )
    CommonAssertions.assert_not_none(
        destination_available_balance_before,
        "Destination pre-transfer available balance should be present.",
    )

    home_page = HomePage(test_context.page, test_context.config_manager)
    accounts_overview_page = home_page.go_to_accounts_overview()

    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_overview_page_loaded(),
        "Accounts Overview Page",
        "Accounts Overview page should be displayed after transfer for balance validation.",
        "transfer_funds_accounts_overview_after_transfer",
    )

    _, source_available_balance_after = _get_account_summary_snapshot(
        accounts_overview_page,
        str(source_account),
    )

    expected_source_available_balance_after = (
        _normalize_decimal(source_available_balance_before) - _normalize_decimal(transfer_amount_decimal)
    ).quantize(Decimal("0.01"))

    expected_destination_balance_after = (
        _normalize_decimal(destination_balance_before) + _normalize_decimal(transfer_amount_decimal)
    ).quantize(Decimal("0.01"))

    destination_balance_after = _wait_for_destination_balance_update(
        test_context,
        str(destination_account),
        expected_destination_balance_after,
    )

    CommonAssertions.assert_equals(
        source_available_balance_after,
        expected_source_available_balance_after,
        "Source available balance did not decrease correctly after transfer.",
    )

    CommonAssertions.assert_equals(
        destination_balance_after,
        expected_destination_balance_after,
        "Destination account balance did not increase correctly after transfer.",
    )
