from __future__ import annotations

from com.parabank.automation.base.base_page import BasePage


class FindTransactionsPage(BasePage):
    PAGE_HEADING = "xpath=//h1[contains(@class,'title') and normalize-space()='Find Transactions']"
    ACCOUNT_DROPDOWN = "#accountId"
    AMOUNT_INPUT = "#amount"
    FIND_BY_AMOUNT_BUTTON = "#findByAmount"
    TRANSACTIONS_TABLE = "#transactionTable"
    TRANSACTION_ROWS = "#transactionTable tbody tr"

    def is_page_heading_visible(self) -> bool:
        return self.is_visible(self.PAGE_HEADING)

    def get_page_heading_text(self) -> str:
        return self.get_text(self.PAGE_HEADING)

    def is_account_dropdown_visible(self) -> bool:
        return self.is_visible(self.ACCOUNT_DROPDOWN)

    def is_amount_input_visible(self) -> bool:
        return self.is_visible(self.AMOUNT_INPUT)

    def is_find_by_amount_button_visible(self) -> bool:
        return self.is_visible(self.FIND_BY_AMOUNT_BUTTON)

    def is_find_transactions_page_loaded(self) -> bool:
        return (
            self.is_page_heading_visible()
            and self.is_account_dropdown_visible()
            and self.is_amount_input_visible()
            and self.is_find_by_amount_button_visible()
        )

    def select_account(self, account_number: str) -> "FindTransactionsPage":
        self.logger.info("Selecting account for transaction search: %s", account_number)
        self.select_dropdown_by_visible_text(self.ACCOUNT_DROPDOWN, account_number)
        return self

    def get_available_accounts(self) -> list[str]:
        return self.get_dropdown_options_text(self.ACCOUNT_DROPDOWN)

    def enter_amount(self, amount: str) -> "FindTransactionsPage":
        self.logger.info("Entering amount for transaction search: %s", amount)
        self.clear_and_enter_text(self.AMOUNT_INPUT, amount)
        return self

    def click_find_by_amount_button(self) -> "FindTransactionsPage":
        self.logger.info("Clicking Find Transactions by amount.")
        self.click(self.FIND_BY_AMOUNT_BUTTON)
        self.wait_for_page_ready()
        return self

    def find_transactions_by_amount(self, account_number: str, amount: str) -> "FindTransactionsPage":
        self.logger.info(
            "Finding transactions by amount. Account=%s | Amount=%s",
            account_number,
            amount,
        )
        return self.select_account(account_number).enter_amount(amount).click_find_by_amount_button()

    def is_transactions_table_visible(self) -> bool:
        return self.is_visible(self.TRANSACTIONS_TABLE)

    def get_transaction_row_count(self) -> int:
        return self.get_count(self.TRANSACTION_ROWS)

    def is_at_least_one_transaction_displayed(self) -> bool:
        return self.get_transaction_row_count() > 0

    def is_matching_amount_displayed(self, amount: str) -> bool:
        normalized_amount = amount.strip()
        possible_values = {
            f"${normalized_amount}",
            f"${normalized_amount}.00",
        }

        cells = self.page.locator("#transactionTable tbody td")
        count = cells.count()

        for index in range(count):
            cell_text = cells.nth(index).inner_text().strip()
            if cell_text in possible_values:
                self.logger.info("Found matching transaction amount in results: %s", cell_text)
                return True

        self.logger.info("No matching transaction amount found in results for amount: %s", amount)
        return False