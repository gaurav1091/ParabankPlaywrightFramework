from __future__ import annotations

import time
from decimal import Decimal

from pytest_bdd import parsers, then, when

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.bill_pay_test_data_provider import BillPayTestDataProvider


def _to_money_decimal(value: str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _generate_unique_bill_payment_amount(base_amount: str) -> Decimal:
    base_decimal = _to_money_decimal(base_amount)
    cents_component = (int(time.time() * 1000) % 90) + 10
    unique_amount = (base_decimal + (Decimal(cents_component) / Decimal("100"))).quantize(Decimal("0.01"))
    return unique_amount


def _to_money_text(value: Decimal) -> str:
    return f"{value:.2f}"


@when("the user navigates to the Bill Pay page")
def navigate_to_bill_pay_page(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before navigating to Bill Pay page.",
    )

    bill_pay_page = home_page.go_to_bill_pay()
    test_context.scenario_context.set("bill_pay_page", bill_pay_page)


@then("the Bill Pay page should be displayed")
def verify_bill_pay_page_displayed(test_context: FrameworkContext) -> None:
    bill_pay_page = test_context.scenario_context.get("bill_pay_page")
    CommonAssertions.assert_not_none(
        bill_pay_page,
        "Bill Pay page should be available in scenario context.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        bill_pay_page.is_bill_pay_page_loaded(),
        "Bill Pay Page",
        "Bill Pay page is not displayed.",
        "bill_pay_page_loaded",
    )
    UiAssertions.assert_text_equals(
        test_context.page,
        bill_pay_page.get_page_heading_text(),
        "Bill Payment Service",
        "Bill Pay page title is incorrect.",
        "bill_pay_page_title",
    )


@when(parsers.parse('the user submits the bill payment using test data key "{test_data_key}"'))
def submit_bill_payment_using_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    bill_pay_page = test_context.scenario_context.get("bill_pay_page")
    CommonAssertions.assert_not_none(
        bill_pay_page,
        "Bill Pay page should be available before bill payment submission.",
    )

    bill_pay_test_data = BillPayTestDataProvider.get_bill_pay_test_data_by_key(test_data_key)
    test_context.scenario_context.set("bill_pay_test_data", bill_pay_test_data)

    submitted_amount_decimal = _generate_unique_bill_payment_amount(bill_pay_test_data.amount)
    submitted_amount_text = _to_money_text(submitted_amount_decimal)

    unique_suffix = str(int(time.time() * 1000))[-6:]
    submitted_payee_name = f"{bill_pay_test_data.payee_name}_{unique_suffix}"

    selected_from_account = bill_pay_page.get_first_valid_from_account()

    bill_pay_page = bill_pay_page.submit_bill_payment(
        payee_name=submitted_payee_name,
        address=bill_pay_test_data.address,
        city=bill_pay_test_data.city,
        state=bill_pay_test_data.state,
        zip_code=bill_pay_test_data.zip_code,
        phone_number=bill_pay_test_data.phone_number,
        account_number=bill_pay_test_data.account_number,
        amount=submitted_amount_text,
    )

    test_context.scenario_context.set("bill_pay_page", bill_pay_page)
    test_context.scenario_context.set("submitted_payee_name", submitted_payee_name)
    test_context.scenario_context.set("selected_from_account", selected_from_account)
    test_context.scenario_context.set("submitted_bill_amount_text", submitted_amount_text)


@then("the bill payment should be completed successfully")
def verify_bill_payment_completed_successfully(test_context: FrameworkContext) -> None:
    bill_pay_page = test_context.scenario_context.get("bill_pay_page")
    submitted_payee_name = test_context.scenario_context.get("submitted_payee_name")
    selected_from_account = test_context.scenario_context.get("selected_from_account")
    submitted_bill_amount_text = test_context.scenario_context.get("submitted_bill_amount_text")

    CommonAssertions.assert_not_none(
        bill_pay_page,
        "Bill Pay page should be available for success validation.",
    )
    CommonAssertions.assert_not_none(
        submitted_payee_name,
        "Submitted payee name should be available for bill pay success validation.",
    )
    CommonAssertions.assert_not_none(
        selected_from_account,
        "Selected source account should be available for bill pay success validation.",
    )
    CommonAssertions.assert_not_none(
        submitted_bill_amount_text,
        "Submitted bill amount should be available for bill pay success validation.",
    )

    UiAssertions.assert_element_visible(
        test_context.page,
        bill_pay_page.is_bill_payment_successful(),
        "Bill Payment Complete Confirmation",
        "Bill payment was not completed successfully.",
        "bill_pay_success",
    )

    heading_text = bill_pay_page.get_bill_payment_complete_heading_text()
    CommonAssertions.assert_true(
        "Bill Payment Complete" in heading_text,
        f"Bill payment success title is incorrect. Actual heading: {heading_text}",
    )

    actual_message = bill_pay_page.get_bill_payment_result_message()
    if actual_message:
        CommonAssertions.assert_contains(
            actual_message,
            submitted_payee_name,
            "Bill payment success message should contain submitted payee name.",
        )
        CommonAssertions.assert_contains(
            actual_message,
            f"${submitted_bill_amount_text}",
            "Bill payment success message should contain submitted bill amount.",
        )
        CommonAssertions.assert_contains(
            actual_message,
            str(selected_from_account),
            "Bill payment success message should contain selected source account.",
        )
