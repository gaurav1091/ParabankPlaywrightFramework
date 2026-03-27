from pytest_bdd import then, when, parsers

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.dataproviders.transfer_funds_test_data_provider import TransferFundsTestDataProvider


@when("the user navigates to the Transfer Funds page")
def navigate_to_transfer_funds_page(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before navigating to Transfer Funds page.",
    )

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
def transfer_funds_using_test_data_key(test_context: FrameworkContext, test_data_key: str) -> None:
    transfer_funds_page = test_context.scenario_context.get("transfer_funds_page")
    CommonAssertions.assert_not_none(
        transfer_funds_page,
        "Transfer Funds page should be available before transfer.",
    )

    transfer_funds_test_data = TransferFundsTestDataProvider.get_transfer_funds_test_data_by_key(test_data_key)
    test_context.scenario_context.set("transfer_funds_test_data", transfer_funds_test_data)

    transfer_funds_page = transfer_funds_page.transfer_funds(transfer_funds_test_data.amount)
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
    UiAssertions.assert_text_equals(
        test_context.page,
        transfer_funds_page.get_transfer_complete_heading_text(),
        "Transfer Complete!",
        "Transfer completion title is incorrect.",
        "transfer_funds_success_title",
    )

    transfer_result_message = transfer_funds_page.get_transfer_result_message()
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

    expected_amount = f"${transfer_funds_test_data.amount}.00"
    actual_amount = transfer_funds_page.get_transferred_amount_value()

    CommonAssertions.assert_equals(
        actual_amount,
        expected_amount,
        "Transferred amount is incorrect.",
    )