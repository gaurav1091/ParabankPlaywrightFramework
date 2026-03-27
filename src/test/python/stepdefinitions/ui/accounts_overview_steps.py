from pytest_bdd import then, when

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext


@when("the user navigates to the Accounts Overview page")
def navigate_to_accounts_overview_page(test_context: FrameworkContext) -> None:
    home_page = test_context.scenario_context.get("home_page")
    CommonAssertions.assert_not_none(
        home_page,
        "Home page should be available before navigating to Accounts Overview page.",
    )

    accounts_overview_page = home_page.go_to_accounts_overview()
    test_context.scenario_context.set("accounts_overview_page", accounts_overview_page)


@then("the accounts overview page should be displayed")
def verify_accounts_overview_displayed(test_context: FrameworkContext) -> None:
    accounts_overview_page = test_context.scenario_context.get("accounts_overview_page")
    CommonAssertions.assert_not_none(
        accounts_overview_page,
        "Accounts Overview page should be available in scenario context.",
    )

    UiAssertions.assert_page_title_contains(
        test_context.page,
        "ParaBank",
        "Accounts Overview page title validation failed.",
        "accounts_overview_title",
    )
    UiAssertions.assert_current_url_contains(
        test_context.page,
        "overview",
        "Accounts Overview URL validation failed.",
        "accounts_overview_url",
    )
    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_page_heading_visible(),
        "Accounts Overview Heading",
        "Accounts Overview heading should be visible.",
        "accounts_overview_heading",
    )
    UiAssertions.assert_element_visible(
        test_context.page,
        accounts_overview_page.is_accounts_table_visible(),
        "Accounts Table",
        "Accounts table should be visible on Accounts Overview page.",
        "accounts_overview_table_visibility",
    )


@then("the accounts table should contain at least one account")
def verify_accounts_table_contains_at_least_one_account(test_context: FrameworkContext) -> None:
    accounts_overview_page = test_context.scenario_context.get("accounts_overview_page")
    CommonAssertions.assert_not_none(
        accounts_overview_page,
        "Accounts Overview page should be available for account table validation.",
    )

    account_row_count = accounts_overview_page.get_account_row_count()
    account_link_count = accounts_overview_page.get_account_link_count()

    CommonAssertions.assert_greater_than(
        account_row_count,
        0,
        "Accounts table should contain at least one row.",
    )
    CommonAssertions.assert_greater_than(
        account_link_count,
        0,
        "Accounts table should contain at least one account link.",
    )