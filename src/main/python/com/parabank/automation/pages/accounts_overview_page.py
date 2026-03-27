from __future__ import annotations

from decimal import Decimal, InvalidOperation

from com.parabank.automation.base.base_page import BasePage


class AccountsOverviewPage(BasePage):
    PAGE_HEADING = "xpath=//h1[normalize-space()='Accounts Overview']"
    ACCOUNTS_TABLE = "#accountTable"
    ACCOUNT_ROWS = "#accountTable tbody tr"
    ACCOUNT_NUMBER_LINKS = "#accountTable tbody tr td:first-child a"

    def is_page_heading_visible(self) -> bool:
        return self.is_visible(self.PAGE_HEADING)

    def get_page_heading_text(self) -> str:
        return self.get_text(self.PAGE_HEADING)

    def is_accounts_table_visible(self) -> bool:
        return self.is_visible(self.ACCOUNTS_TABLE)

    def is_accounts_overview_page_loaded(self) -> bool:
        return self.is_page_heading_visible() and self.is_accounts_table_visible()

    def get_account_row_count(self) -> int:
        return self.get_count(self.ACCOUNTS_TABLE + " tbody tr")

    def get_account_link_count(self) -> int:
        return self.get_count(self.ACCOUNT_NUMBER_LINKS)

    def has_at_least_one_account(self) -> bool:
        return self.get_account_link_count() > 0

    def get_account_numbers(self) -> list[str]:
        rows = self.page.locator(self.ACCOUNT_ROWS)
        row_count = rows.count()

        account_numbers: list[str] = []
        for index in range(row_count):
            row = rows.nth(index)
            cells = row.locator("td")
            if cells.count() < 1:
                continue

            account_number = cells.nth(index=0).inner_text().strip()
            if account_number and account_number.lower() != "total":
                account_numbers.append(account_number)

        self.logger.info("Account numbers found on Accounts Overview page: %s", account_numbers)
        return account_numbers

    def get_new_account_numbers_since(self, existing_account_numbers: list[str]) -> list[str]:
        current_account_numbers = self.get_account_numbers()
        existing_set = {str(account_number).strip() for account_number in existing_account_numbers}
        new_accounts = [account for account in current_account_numbers if account not in existing_set]

        self.logger.info(
            "New account numbers since baseline. Existing=%s | Current=%s | New=%s",
            existing_account_numbers,
            current_account_numbers,
            new_accounts,
        )
        return new_accounts

    def get_latest_new_account_number_since(self, existing_account_numbers: list[str]) -> str | None:
        new_accounts = self.get_new_account_numbers_since(existing_account_numbers)
        if not new_accounts:
            return None
        return new_accounts[-1]

    def get_accounts_summary(self) -> list[dict[str, object]]:
        self.logger.info("Reading account summary from Accounts Overview table.")
        self.wait_for_page_ready()

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

            if not account_number or account_number.lower() == "total":
                self.logger.info(
                    "Skipping Accounts Overview row because it is not an account row. RowIndex=%s | Account=%s",
                    index,
                    account_number,
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

    def get_account_summary_by_number(self, account_number: str) -> dict[str, object]:
        normalized_target = str(account_number).strip()

        for account in self.get_accounts_summary():
            if str(account["account_number"]).strip() == normalized_target:
                self.logger.info("Account summary found for account number: %s", normalized_target)
                return account

        raise AssertionError(f"Account number '{normalized_target}' was not found on Accounts Overview page.")

    def get_balance_for_account(self, account_number: str) -> Decimal:
        account_summary = self.get_account_summary_by_number(account_number)
        balance = account_summary["balance"]

        if not isinstance(balance, Decimal):
            raise AssertionError(f"Balance for account '{account_number}' is not a Decimal value.")

        self.logger.info("Balance for account %s is %s", account_number, balance)
        return balance

    def get_available_balance_for_account(self, account_number: str) -> Decimal:
        account_summary = self.get_account_summary_by_number(account_number)
        available_balance = account_summary["available_balance"]

        if not isinstance(available_balance, Decimal):
            raise AssertionError(f"Available balance for account '{account_number}' is not a Decimal value.")

        self.logger.info("Available balance for account %s is %s", account_number, available_balance)
        return available_balance

    def get_first_account_number(self) -> str:
        account_numbers = self.get_account_numbers()
        if not account_numbers:
            raise RuntimeError("No account numbers are available on Accounts Overview page.")
        return account_numbers[0]

    def get_first_healthy_account_number(self, minimum_available_balance: float | int | str = 1) -> str:
        minimum_balance = Decimal(str(minimum_available_balance))
        accounts = self.get_accounts_summary()

        for account in accounts:
            available_balance = account["available_balance"]
            if isinstance(available_balance, Decimal) and available_balance >= minimum_balance:
                selected_account = str(account["account_number"])
                self.logger.info(
                    "Selected healthy account from Accounts Overview. Account=%s | Available=%s",
                    selected_account,
                    available_balance,
                )
                return selected_account

        raise AssertionError(
            f"No account found with minimum available balance >= {minimum_balance} on Accounts Overview page."
        )

    def get_eligible_source_accounts_for_new_account(
        self,
        minimum_available_balance: float | int | str = 10,
    ) -> list[str]:
        minimum_balance = Decimal(str(minimum_available_balance))
        accounts = self.get_accounts_summary()

        eligible_accounts: list[tuple[str, Decimal]] = []

        for account in accounts:
            account_number = str(account["account_number"])
            available_balance = account["available_balance"]

            if isinstance(available_balance, Decimal) and available_balance >= minimum_balance:
                eligible_accounts.append((account_number, available_balance))

        eligible_accounts.sort(key=lambda item: (item[1], item[0]))
        ordered_account_numbers = [account_number for account_number, _ in eligible_accounts]

        self.logger.info(
            "Eligible source accounts for new account opening (minimum=%s): %s",
            minimum_balance,
            ordered_account_numbers,
        )

        if not ordered_account_numbers:
            raise AssertionError(
                f"No eligible source accounts found with available balance >= {minimum_balance} "
                f"on Accounts Overview page."
            )

        return ordered_account_numbers

    def get_transfer_candidate_accounts(self, transfer_amount: float | int | str) -> tuple[str, str]:
        transfer_amount_decimal = Decimal(str(transfer_amount)).quantize(Decimal("0.01"))
        accounts = self.get_accounts_summary()

        source_candidates = [
            account
            for account in accounts
            if isinstance(account["available_balance"], Decimal)
            and account["available_balance"] >= transfer_amount_decimal
        ]

        source_candidates.sort(key=lambda item: (item["available_balance"], str(item["account_number"])))
        all_accounts_sorted = sorted(accounts, key=lambda item: str(item["account_number"]))

        for source_account in source_candidates:
            source_account_number = str(source_account["account_number"])

            for destination_account in all_accounts_sorted:
                destination_account_number = str(destination_account["account_number"])

                if destination_account_number != source_account_number:
                    self.logger.info(
                        "Selected transfer candidate accounts. Amount=%s | From=%s | To=%s",
                        transfer_amount_decimal,
                        source_account_number,
                        destination_account_number,
                    )
                    return source_account_number, destination_account_number

        raise AssertionError(
            f"No valid source/destination account pair found for transfer amount {transfer_amount_decimal}."
        )

    def _parse_currency(self, currency_value: str) -> Decimal:
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
            return Decimal(normalized).quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError) as exc:
            raise AssertionError(
                f"Unable to parse currency value from Accounts Overview: '{currency_value}'"
            ) from exc