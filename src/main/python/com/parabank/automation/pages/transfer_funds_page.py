from __future__ import annotations

from com.parabank.automation.base.base_page import BasePage


class TransferFundsPage(BasePage):
    PAGE_HEADING = "css=div#showForm h1.title"
    AMOUNT_INPUT = "#amount"
    FROM_ACCOUNT_DROPDOWN = "#fromAccountId"
    TO_ACCOUNT_DROPDOWN = "#toAccountId"
    TRANSFER_BUTTON = "input[value='Transfer']"

    TRANSFER_COMPLETE_HEADING = "css=div#showResult h1.title"
    TRANSFER_RESULT_MESSAGE = "css=div#showResult p"
    TRANSFERRED_AMOUNT_VALUE = "#amountResult"
    FROM_ACCOUNT_RESULT_VALUE = "#fromAccountIdResult"
    TO_ACCOUNT_RESULT_VALUE = "#toAccountIdResult"

    def is_page_heading_visible(self) -> bool:
        return self.is_visible(self.PAGE_HEADING)

    def get_page_heading_text(self) -> str:
        return self.get_text(self.PAGE_HEADING)

    def is_amount_input_visible(self) -> bool:
        return self.is_visible(self.AMOUNT_INPUT)

    def is_from_account_dropdown_visible(self) -> bool:
        return self.is_visible(self.FROM_ACCOUNT_DROPDOWN)

    def is_to_account_dropdown_visible(self) -> bool:
        return self.is_visible(self.TO_ACCOUNT_DROPDOWN)

    def is_transfer_button_visible(self) -> bool:
        return self.is_visible(self.TRANSFER_BUTTON)

    def is_transfer_funds_page_loaded(self) -> bool:
        return (
            self.is_page_heading_visible()
            and self.is_amount_input_visible()
            and self.is_from_account_dropdown_visible()
            and self.is_to_account_dropdown_visible()
            and self.is_transfer_button_visible()
        )

    def enter_amount(self, amount: str) -> "TransferFundsPage":
        self.logger.info("Entering transfer amount: %s", amount)
        self.clear_and_enter_text(self.AMOUNT_INPUT, amount)
        return self

    def select_from_account(self, account_number: str) -> "TransferFundsPage":
        self.logger.info("Selecting source account for transfer: %s", account_number)
        self.select_dropdown_by_visible_text(self.FROM_ACCOUNT_DROPDOWN, account_number)
        return self

    def select_to_account(self, account_number: str) -> "TransferFundsPage":
        self.logger.info("Selecting destination account for transfer: %s", account_number)
        self.select_dropdown_by_visible_text(self.TO_ACCOUNT_DROPDOWN, account_number)
        return self

    def select_first_available_accounts(self) -> "TransferFundsPage":
        self.logger.info("Selecting first available valid source and destination accounts.")

        selected_from_account = self.select_first_valid_dropdown_option(self.FROM_ACCOUNT_DROPDOWN)
        available_to_accounts = self.get_available_to_accounts()

        for account in available_to_accounts:
            if account != selected_from_account:
                self.select_dropdown_by_visible_text(self.TO_ACCOUNT_DROPDOWN, account)
                self.logger.info(
                    "Selected transfer accounts. From=%s | To=%s",
                    selected_from_account,
                    account,
                )
                return self

        if available_to_accounts:
            fallback_account = available_to_accounts[0]
            self.select_dropdown_by_visible_text(self.TO_ACCOUNT_DROPDOWN, fallback_account)
            self.logger.info(
                "Fallback transfer account selection. From=%s | To=%s",
                selected_from_account,
                fallback_account,
            )
            return self

        raise RuntimeError("No valid destination account available in transfer dropdown.")

    def get_available_from_accounts(self) -> list[str]:
        return self.get_dropdown_options_text(self.FROM_ACCOUNT_DROPDOWN)

    def get_available_to_accounts(self) -> list[str]:
        return self.get_dropdown_options_text(self.TO_ACCOUNT_DROPDOWN)

    def get_selected_from_account(self) -> str:
        return self.get_selected_dropdown_text(self.FROM_ACCOUNT_DROPDOWN)

    def get_selected_to_account(self) -> str:
        return self.get_selected_dropdown_text(self.TO_ACCOUNT_DROPDOWN)

    def click_transfer_button(self) -> "TransferFundsPage":
        self.logger.info("Clicking Transfer button.")
        self.click(self.TRANSFER_BUTTON)
        self.wait_for_page_ready()
        return self

    def transfer_funds(self, amount: str) -> "TransferFundsPage":
        self.logger.info("Executing transfer flow for amount: %s", amount)
        return self.enter_amount(amount).select_first_available_accounts().click_transfer_button()

    def transfer_funds_between_accounts(
        self,
        amount: str,
        from_account: str,
        to_account: str,
    ) -> "TransferFundsPage":
        self.logger.info(
            "Executing transfer flow with explicit accounts. Amount=%s | From=%s | To=%s",
            amount,
            from_account,
            to_account,
        )
        return (
            self.enter_amount(amount)
            .select_from_account(from_account)
            .select_to_account(to_account)
            .click_transfer_button()
        )

    def is_transfer_successful(self) -> bool:
        return self.is_visible(self.TRANSFER_COMPLETE_HEADING) and self.is_visible(self.TRANSFER_RESULT_MESSAGE)

    def get_transfer_complete_heading_text(self) -> str:
        return self.get_text(self.TRANSFER_COMPLETE_HEADING)

    def get_transfer_result_message(self) -> str:
        return self.get_text(self.TRANSFER_RESULT_MESSAGE)

    def get_transferred_amount_value(self) -> str:
        return self.get_text(self.TRANSFERRED_AMOUNT_VALUE)

    def get_result_from_account_value(self) -> str:
        return self.get_text(self.FROM_ACCOUNT_RESULT_VALUE)

    def get_result_to_account_value(self) -> str:
        return self.get_text(self.TO_ACCOUNT_RESULT_VALUE)