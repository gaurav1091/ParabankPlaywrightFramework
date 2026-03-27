from __future__ import annotations

from decimal import Decimal, InvalidOperation

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

    def get_transaction_rows_data(self) -> list[dict[str, str]]:
        self.logger.info("Reading transaction result rows from Find Transactions table.")

        rows = self.page.locator(self.TRANSACTION_ROWS)
        row_count = rows.count()

        transactions: list[dict[str, str]] = []

        for index in range(row_count):
            row = rows.nth(index)
            cells = row.locator("td")
            cell_count = cells.count()

            if cell_count < 4:
                self.logger.info(
                    "Skipping Find Transactions row because it has fewer than 4 cells. RowIndex=%s | CellCount=%s",
                    index,
                    cell_count,
                )
                continue

            row_data = {
                "date": cells.nth(0).inner_text().strip(),
                "transaction": cells.nth(1).inner_text().strip(),
                "debit": cells.nth(2).inner_text().strip(),
                "credit": cells.nth(3).inner_text().strip(),
            }
            transactions.append(row_data)

            self.logger.info(
                "Transaction result row captured. RowIndex=%s | Date=%s | Transaction=%s | Debit=%s | Credit=%s",
                index,
                row_data["date"],
                row_data["transaction"],
                row_data["debit"],
                row_data["credit"],
            )

        return transactions

    def get_displayed_transaction_amounts(self) -> list[Decimal]:
        transactions = self.get_transaction_rows_data()
        amounts: list[Decimal] = []

        for transaction in transactions:
            debit_value = self._parse_currency_or_none(transaction["debit"])
            credit_value = self._parse_currency_or_none(transaction["credit"])

            if debit_value is not None:
                amounts.append(abs(debit_value))
            if credit_value is not None:
                amounts.append(abs(credit_value))

        self.logger.info("Displayed transaction amounts parsed from results: %s", amounts)
        return amounts

    def is_matching_amount_displayed(self, amount: str) -> bool:
        expected_amount = Decimal(str(amount)).quantize(Decimal("0.01"))
        displayed_amounts = self.get_displayed_transaction_amounts()

        for displayed_amount in displayed_amounts:
            if displayed_amount == expected_amount:
                self.logger.info("Found matching transaction amount in results: %s", displayed_amount)
                return True

        self.logger.info("No matching transaction amount found in results for amount: %s", expected_amount)
        return False

    def are_all_displayed_transaction_amounts_matching(self, amount: str) -> bool:
        expected_amount = Decimal(str(amount)).quantize(Decimal("0.01"))
        displayed_amounts = self.get_displayed_transaction_amounts()

        if not displayed_amounts:
            self.logger.info("No displayed transaction amounts found for validation.")
            return False

        all_match = all(displayed_amount == expected_amount for displayed_amount in displayed_amounts)
        self.logger.info(
            "All displayed transaction amounts matching expected=%s ? %s | Displayed=%s",
            expected_amount,
            all_match,
            displayed_amounts,
        )
        return all_match

    def is_transaction_search_result_correct(self, amount: str) -> bool:
        return (
            self.is_transactions_table_visible()
            and self.is_at_least_one_transaction_displayed()
            and self.is_matching_amount_displayed(amount)
            and self.are_all_displayed_transaction_amounts_matching(amount)
        )

    def _parse_currency_or_none(self, currency_value: str) -> Decimal | None:
        if currency_value is None:
            return None

        cleaned = currency_value.strip()
        if not cleaned:
            return None

        normalized = (
            cleaned.replace("$", "")
            .replace(",", "")
            .replace("(", "-")
            .replace(")", "")
        )

        if not normalized:
            return None

        try:
            return Decimal(normalized).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            return None