from __future__ import annotations

from com.parabank.automation.base.base_page import BasePage


class OpenNewAccountPage(BasePage):
    PAGE_HEADING = "css=div#openAccountForm h1.title"
    ACCOUNT_TYPE_DROPDOWN = "#type"
    FROM_ACCOUNT_DROPDOWN = "#fromAccountId"
    OPEN_NEW_ACCOUNT_BUTTON = "button.button, input.button"
    ACCOUNT_OPENED_HEADING = "css=div#openAccountResult h1.title"
    NEW_ACCOUNT_NUMBER_LINK = "#newAccountId"

    def is_page_heading_visible(self) -> bool:
        return self.is_visible(self.PAGE_HEADING)

    def get_page_heading_text(self) -> str:
        return self.get_text(self.PAGE_HEADING)

    def is_account_type_dropdown_visible(self) -> bool:
        return self.is_visible(self.ACCOUNT_TYPE_DROPDOWN)

    def is_from_account_dropdown_visible(self) -> bool:
        return self.is_visible(self.FROM_ACCOUNT_DROPDOWN)

    def is_open_new_account_button_visible(self) -> bool:
        return self.is_visible(self.OPEN_NEW_ACCOUNT_BUTTON)

    def is_open_new_account_page_loaded(self) -> bool:
        return (
            self.is_page_heading_visible()
            and self.is_account_type_dropdown_visible()
            and self.is_from_account_dropdown_visible()
            and self.is_open_new_account_button_visible()
        )

    def select_account_type(self, account_type: str) -> "OpenNewAccountPage":
        self.logger.info("Selecting account type: %s", account_type)
        self.select_dropdown_by_visible_text(self.ACCOUNT_TYPE_DROPDOWN, account_type)
        return self

    def get_available_account_types(self) -> list[str]:
        return self.get_dropdown_options_text(self.ACCOUNT_TYPE_DROPDOWN)

    def select_first_available_from_account(self) -> "OpenNewAccountPage":
        self.logger.info("Selecting first available source account.")
        self.select_first_valid_dropdown_option(self.FROM_ACCOUNT_DROPDOWN)
        return self

    def select_from_account(self, account_number: str) -> "OpenNewAccountPage":
        self.logger.info("Selecting source account: %s", account_number)
        self.select_dropdown_by_visible_text(self.FROM_ACCOUNT_DROPDOWN, account_number)
        return self

    def get_available_from_accounts(self) -> list[str]:
        return self.get_dropdown_options_text(self.FROM_ACCOUNT_DROPDOWN)

    def get_selected_from_account(self) -> str:
        return self.get_selected_dropdown_text(self.FROM_ACCOUNT_DROPDOWN)

    def click_open_new_account_button(self) -> "OpenNewAccountPage":
        self.logger.info("Clicking Open New Account button.")
        self.click(self.OPEN_NEW_ACCOUNT_BUTTON)
        self.wait_for_page_ready()
        return self

    def open_new_account(self, account_type: str) -> "OpenNewAccountPage":
        self.logger.info("Opening new account with type: %s", account_type)
        return self.select_account_type(account_type).select_first_available_from_account().click_open_new_account_button()

    def open_new_account_from_specific_source(self, account_type: str, from_account: str) -> "OpenNewAccountPage":
        self.logger.info(
            "Opening new account with type=%s using specific source account=%s",
            account_type,
            from_account,
        )
        return self.select_account_type(account_type).select_from_account(from_account).click_open_new_account_button()

    def is_account_creation_successful(self) -> bool:
        return self.is_visible(self.ACCOUNT_OPENED_HEADING) and self.is_visible(self.NEW_ACCOUNT_NUMBER_LINK)

    def get_account_opened_heading_text(self) -> str:
        return self.get_text(self.ACCOUNT_OPENED_HEADING)

    def is_new_account_number_visible(self) -> bool:
        return self.is_visible(self.NEW_ACCOUNT_NUMBER_LINK)

    def get_new_account_number(self) -> str:
        return self.get_text(self.NEW_ACCOUNT_NUMBER_LINK).strip()