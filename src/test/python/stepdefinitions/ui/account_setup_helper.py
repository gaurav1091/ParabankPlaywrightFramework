from __future__ import annotations

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.pages.home_page import HomePage

MINIMUM_SOURCE_ACCOUNT_BALANCE_FOR_NEW_ACCOUNT = 10
DEFAULT_NEW_ACCOUNT_TYPE = "SAVINGS"


def ensure_at_least_two_accounts_for_transfer(test_context: FrameworkContext) -> list[str]:
    """
    Ensure the logged-in user has at least two accounts.
    Transfer Funds and the setup-transfer inside Find Transactions
    require distinct source and destination accounts.

    Strategy:
    1. Read Accounts Overview.
    2. If two or more accounts already exist, return immediately.
    3. Otherwise, open a new account from a healthy source account.
    4. Re-check Accounts Overview and confirm a new account now exists.
    """
    home_page = HomePage(test_context.page, test_context.config_manager)

    accounts_overview_page = home_page.go_to_accounts_overview()
    baseline_account_numbers = accounts_overview_page.get_account_numbers()

    if len(set(baseline_account_numbers)) >= 2:
        return baseline_account_numbers

    source_account = accounts_overview_page.get_first_healthy_account_number(
        MINIMUM_SOURCE_ACCOUNT_BALANCE_FOR_NEW_ACCOUNT
    )

    open_new_account_page = home_page.go_to_open_new_account()
    available_account_types = open_new_account_page.get_available_account_types()

    normalized_account_types = [
        account_type.strip().upper()
        for account_type in available_account_types
        if account_type and account_type.strip()
    ]

    if DEFAULT_NEW_ACCOUNT_TYPE in normalized_account_types:
        account_type_to_create = DEFAULT_NEW_ACCOUNT_TYPE
    else:
        CommonAssertions.assert_true(
            len(normalized_account_types) > 0,
            "No account types are available on Open New Account page.",
        )
        account_type_to_create = normalized_account_types[0]

    open_new_account_page = home_page.go_to_open_new_account()
    open_new_account_page.open_new_account_from_specific_source(
        account_type=account_type_to_create,
        from_account=source_account,
    )

    accounts_overview_page = home_page.go_to_accounts_overview()
    current_account_numbers = accounts_overview_page.get_account_numbers()

    CommonAssertions.assert_true(
        len(set(current_account_numbers)) >= 2,
        "At least two accounts should exist after automatic account setup for transfer-capable flows. "
        f"Before={baseline_account_numbers} | After={current_account_numbers}",
    )

    new_accounts = accounts_overview_page.get_new_account_numbers_since(baseline_account_numbers)
    CommonAssertions.assert_true(
        len(new_accounts) >= 1,
        "Automatic account setup did not create a detectable new account. "
        f"Before={baseline_account_numbers} | After={current_account_numbers}",
    )

    test_context.scenario_context.set("auto_created_transfer_support_account", new_accounts[-1])
    return current_account_numbers