from __future__ import annotations

from decimal import Decimal, InvalidOperation

from com.parabank.automation.base.base_page import BasePage
from com.parabank.automation.utils.wait_utils import WaitUtils


class AccountsOverviewPage(BasePage):
    PAGE_HEADING = "xpath=//h1[normalize-space()='Accounts Overview']"
    ACCOUNTS_TABLE = "#accountTable"
    ACCOUNT_ROWS = "#accountTable tbody tr"

    def is_page_heading_visible(self) -> bool:
        return self.is_visible(self.PAGE_HEADING)

    def is_accounts_table_visible(self) -> bool:
        return self.is_visible(self.ACCOUNTS_TABLE)

    def is_accounts_overview_page_loaded(self) -> bool:
        return self.is_page_heading_visible() and self.is_accounts_table_visible()

    def get_account_row_count(self) -> int:
        return self.get_count(self.ACCOUNT_ROWS)

    def has_at_least_one_account(self) -> bool:
        return self.get_account_row_count() > 0

    def get_account_numbers(self) -> list[str]:
        rows = self.page.locator(self.ACCOUNT_ROWS)
        row_count = rows.count()

        account_numbers: list[str] = []
        for index in range(row_count):
            row = rows.nth(index)
            cells = row.locator("td")
            if cells.count() < 1:
                continue

            account_number = cells.nth(0).inner_text().strip()
            if account_number:
                account_numbers.append(account_number)

        return account_numbers

    def get_accounts_summary(self) -> list[dict[str, object]]:
        self.logger.info("Reading account summary from Accounts Overview table.")

        WaitUtils.wait_for_page_load(self.page, self.config_manager)
        rows = self.page.locator(self.ACCOUNT_ROWS)
        row_count = rows.count()

        accounts: list[dict[str, object]] = []

        for index in range(row_count):
            row = rows.nth(index)
            cells = row.locator("td")
            cell_count = cells.count()

            if cell_count < 3:
                self.logger.info(
                    "Skipping Accounts Overview row because it has fewer than 3 cells. RowIndex=%s | CellCount=%s",
                    index,
                    cell_count,
                )
                continue

            account_number = cells.nth(0).inner_text().strip()
            balance_text = cells.nth(1).inner_text().strip()
            available_balance_text = cells.nth(2).inner_text().strip()

            if not account_number:
                self.logger.info(
                    "Skipping Accounts Overview row because account number is blank. RowIndex=%s",
                    index,
                )
                continue

            if not balance_text or not available_balance_text:
                self.logger.info(
                    "Skipping Accounts Overview row because balance data is incomplete. "
                    "RowIndex=%s | Account=%s | Balance='%s' | Available='%s'",
                    index,
                    account_number,
                    balance_text,
                    available_balance_text,
                )
                continue

            balance = self._parse_currency(balance_text)
            available_balance = self._parse_currency(available_balance_text)

            account_info = {
                "account_number": account_number,
                "balance_text": balance_text,
                "available_balance_text": available_balance_text,
                "balance": balance,
                "available_balance": available_balance,
            }
            accounts.append(account_info)

            self.logger.info(
                "Account summary row captured. Account=%s | Balance=%s | Available=%s",
                account_number,
                balance_text,
                available_balance_text,
            )

        return accounts

    def get_candidate_source_accounts_for_new_account(
        self,
        minimum_amount: float | int | str,
        preferred_minimum_amount: float | int | str = 100,
        anomaly_balance_threshold: float | int | str = 100000,
    ) -> list[str]:
        minimum_balance = Decimal(str(minimum_amount))
        preferred_minimum_balance = Decimal(str(preferred_minimum_amount))
        anomaly_threshold = Decimal(str(anomaly_balance_threshold))

        accounts = self.get_accounts_summary()

        eligible_accounts: list[dict[str, object]] = []
        for account in accounts:
            available_balance = account["available_balance"]
            if not isinstance(available_balance, Decimal):
                continue

            if available_balance < minimum_balance:
                continue

            if available_balance <= Decimal("0"):
                continue

            eligible_accounts.append(account)

        if not eligible_accounts:
            available_snapshot = ", ".join(
                f"{account['account_number']}={account['available_balance_text']}" for account in accounts
            ) or "No accounts found"

            raise AssertionError(
                "No account has sufficient available balance for opening a new account. "
                f"Required minimum={minimum_balance} | Accounts={available_snapshot}"
            )

        normal_accounts = [
            account
            for account in eligible_accounts
            if isinstance(account["available_balance"], Decimal)
            and account["available_balance"] < anomaly_threshold
        ]

        preferred_accounts = [
            account
            for account in normal_accounts
            if isinstance(account["available_balance"], Decimal)
            and account["available_balance"] >= preferred_minimum_balance
        ]

        fallback_accounts = [
            account for account in normal_accounts
            if account not in preferred_accounts
        ]

        anomalous_accounts = [
            account for account in eligible_accounts
            if account not in normal_accounts
        ]

        preferred_accounts.sort(
            key=lambda account: (
                account["available_balance"],
                str(account["account_number"]),
            )
        )
        fallback_accounts.sort(
            key=lambda account: (
                account["available_balance"],
                str(account["account_number"]),
            )
        )
        anomalous_accounts.sort(
            key=lambda account: (
                account["available_balance"],
                str(account["account_number"]),
            )
        )

        ordered_candidates = preferred_accounts + fallback_accounts + anomalous_accounts
        candidate_numbers = [str(account["account_number"]) for account in ordered_candidates]

        self.logger.info(
            "Candidate source accounts for opening new account: %s",
            ", ".join(
                f"{account['account_number']}={account['available_balance_text']}"
                for account in ordered_candidates
            ),
        )

        return candidate_numbers

    def _parse_currency(self, currency_value: str) -> Decimal:
        if currency_value is None:
            raise AssertionError("Currency value is None and cannot be parsed.")

        normalized = (
            currency_value.strip()
            .replace("$", "")
            .replace(",", "")
            .replace("(", "-")
            .replace(")", "")
        )

        if not normalized:
            raise AssertionError("Currency value is blank and cannot be parsed.")

        try:
            return Decimal(normalized)
        except (InvalidOperation, ValueError) as exc:
            raise AssertionError(
                f"Unable to parse currency value from Accounts Overview: '{currency_value}'"
            ) from exc