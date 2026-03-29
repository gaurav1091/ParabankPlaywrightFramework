from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from com.parabank.automation.base.base_page import BasePage


class FindTransactionsPage(BasePage):
    PAGE_HEADING = "xpath=//h1[contains(@class,'title') and normalize-space()='Find Transactions']"
    ACCOUNT_DROPDOWN = "#accountId"
    AMOUNT_INPUT = "#amount"
    FIND_BY_AMOUNT_BUTTON = "#findByAmount"

    TRANSACTIONS_TABLE = "#transactionTable"
    TRANSACTION_ROWS = "#transactionTable tbody tr"
    NO_TRANSACTIONS_MESSAGE = (
        "xpath=//*[contains(normalize-space(),'No transactions found')]"
        " | "
        "//*[contains(normalize-space(),'Transaction results not found')]"
        " | "
        "//*[contains(normalize-space(),'No transactions')]"
    )

    AMOUNT_PATTERN = re.compile(r"\$-?\d[\d,]*\.\d{2}")

    def is_find_transactions_page_loaded(self) -> bool:
        return (
            self.is_visible(self.PAGE_HEADING)
            and self.is_visible(self.ACCOUNT_DROPDOWN)
            and self.is_visible(self.AMOUNT_INPUT)
            and self.is_visible(self.FIND_BY_AMOUNT_BUTTON)
        )

    def get_page_heading_text(self) -> str:
        return self.get_text(self.PAGE_HEADING).strip()

    def select_account(self, account_number: str) -> "FindTransactionsPage":
        self.logger.info("Selecting account for transaction search: %s", account_number)
        self.select_dropdown_by_visible_text(self.ACCOUNT_DROPDOWN, account_number)
        return self

    def enter_amount(self, amount: str) -> "FindTransactionsPage":
        self.logger.info("Entering amount for transaction search: %s", amount)
        self.clear_and_enter_text(self.AMOUNT_INPUT, amount)
        return self

    def click_find_by_amount(self) -> "FindTransactionsPage":
        self.logger.info("Clicking Find Transactions by amount.")
        self.click(self.FIND_BY_AMOUNT_BUTTON)
        self._wait_for_search_outcome()
        return self

    def find_transactions_by_amount(self, account_number: str, amount: str) -> "FindTransactionsPage":
        self.logger.info("Finding transactions by amount. Account=%s | Amount=%s", account_number, amount)
        return self.select_account(account_number).enter_amount(amount).click_find_by_amount()

    def is_transactions_table_visible(self) -> bool:
        self._wait_for_search_outcome()
        return self.is_visible(self.TRANSACTIONS_TABLE)

    def is_no_transactions_message_visible(self) -> bool:
        self._wait_for_search_outcome()
        return self.is_visible(self.NO_TRANSACTIONS_MESSAGE)

    def get_no_transactions_message_text(self) -> str:
        self._wait_for_search_outcome()
        if self.is_visible(self.NO_TRANSACTIONS_MESSAGE):
            return self.get_text(self.NO_TRANSACTIONS_MESSAGE).strip()
        return ""

    def is_at_least_one_transaction_displayed(self) -> bool:
        self._wait_for_search_outcome()
        if not self.is_visible(self.TRANSACTIONS_TABLE):
            return False
        return self.get_count(self.TRANSACTION_ROWS) > 0

    def get_displayed_transaction_amounts(self) -> list[str]:
        self._wait_for_search_outcome()

        if not self.is_visible(self.TRANSACTIONS_TABLE):
            return []

        rows = self.page.locator(self.TRANSACTION_ROWS)
        row_count = rows.count()
        displayed_amounts: list[str] = []

        for index in range(row_count):
            row = rows.nth(index)
            row_text = row.inner_text().strip()
            self.logger.info("Transaction result row %s text: %s", index, row_text)

            matches = self.AMOUNT_PATTERN.findall(row_text)
            if matches:
                amount_text = matches[-1].strip()
                displayed_amounts.append(amount_text)

        self.logger.info("Displayed transaction amounts: %s", displayed_amounts)
        return displayed_amounts

    def is_matching_amount_displayed(self, expected_amount: str) -> bool:
        normalized_expected = self._normalize_amount(expected_amount)
        displayed_amounts = self.get_displayed_transaction_amounts()

        for actual_amount in displayed_amounts:
            if self._normalize_amount(actual_amount) == normalized_expected:
                return True
        return False

    def are_all_displayed_transaction_amounts_matching(self, expected_amount: str) -> bool:
        normalized_expected = self._normalize_amount(expected_amount)
        displayed_amounts = self.get_displayed_transaction_amounts()

        if not displayed_amounts:
            return False

        return all(self._normalize_amount(actual_amount) == normalized_expected for actual_amount in displayed_amounts)

    def is_transaction_search_result_correct(self, expected_amount: str) -> bool:
        return self.is_at_least_one_transaction_displayed() and self.are_all_displayed_transaction_amounts_matching(
            expected_amount
        )

    def _normalize_amount(self, amount: str) -> str:
        raw_value = str(amount).strip().replace("$", "").replace(",", "")
        try:
            normalized = Decimal(raw_value).quantize(Decimal("0.00"))
            return format(normalized, ".2f")
        except (InvalidOperation, ValueError) as exc:
            raise AssertionError(f"Unable to normalize transaction amount value: '{amount}'") from exc

    def _wait_for_search_outcome(self) -> None:
        self.wait_for_page_ready()
        self.page.wait_for_timeout(1200)

        try:
            self.get_locator(self.TRANSACTIONS_TABLE).wait_for(
                state="visible",
                timeout=3500,
            )
            self.logger.info("Transactions table became visible.")
            return
        except Exception:
            self.logger.info("Transactions table not visible yet. Checking no-results message.")

        try:
            self.get_locator(self.NO_TRANSACTIONS_MESSAGE).wait_for(
                state="visible",
                timeout=2500,
            )
            self.logger.info("No-transactions message became visible.")
            return
        except Exception:
            self.logger.info("No-transactions message not visible. Final state will be inferred from page content.")

        self.logger.info(
            "Find Transactions search outcome. URL=%s | Title=%s",
            self.get_current_url(),
            self.get_title(),
        )
