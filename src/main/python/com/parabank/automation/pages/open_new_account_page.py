from playwright.sync_api import Locator

from com.parabank.automation.base.base_page import BasePage
from com.parabank.automation.utils.wait_utils import WaitUtils


class OpenNewAccountPage(BasePage):
    PAGE_HEADING = "xpath=//h1[normalize-space()='Open New Account']"
    ACCOUNT_TYPE_DROPDOWN = "#type"
    FROM_ACCOUNT_DROPDOWN = "#fromAccountId"
    OPEN_NEW_ACCOUNT_BUTTON = "button.button, input.button"
    ACCOUNT_OPENED_HEADING = "xpath=//h1[normalize-space()='Account Opened!']"
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
        dropdown = self.page.locator(self.ACCOUNT_TYPE_DROPDOWN)
        dropdown.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        dropdown.select_option(
            label=account_type,
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        return self

    def get_available_account_types(self) -> list[str]:
        dropdown = self.page.locator(self.ACCOUNT_TYPE_DROPDOWN)
        dropdown.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )

        options = dropdown.locator("option")
        count = options.count()

        account_types: list[str] = []
        for index in range(count):
            text = options.nth(index).inner_text().strip()
            if text:
                account_types.append(text)

        return account_types

    def select_first_available_from_account(self) -> "OpenNewAccountPage":
        self.logger.info("Selecting first available source account.")
        dropdown = self.page.locator(self.FROM_ACCOUNT_DROPDOWN)
        dropdown.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )

        selected_value = self._select_first_valid_option(dropdown)
        if selected_value is None:
            raise RuntimeError("No source account is available in the Open New Account dropdown.")

        return self

    def get_selected_from_account(self) -> str:
        dropdown = self.page.locator(self.FROM_ACCOUNT_DROPDOWN)
        dropdown.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )

        selected_text = dropdown.locator("option:checked").inner_text().strip()
        self.logger.info("Selected source account: %s", selected_text)
        return selected_text

    def click_open_new_account_button(self) -> "OpenNewAccountPage":
        self.logger.info("Clicking Open New Account button.")
        self.click(self.OPEN_NEW_ACCOUNT_BUTTON)
        WaitUtils.wait_for_page_load(self.page, self.config_manager)
        return self

    def open_new_account(self, account_type: str) -> "OpenNewAccountPage":
        self.logger.info("Opening new account with type: %s", account_type)
        return (
            self.select_account_type(account_type)
            .select_first_available_from_account()
            .click_open_new_account_button()
        )

    def is_account_creation_successful(self) -> bool:
        return self.is_visible(self.ACCOUNT_OPENED_HEADING) and self.is_visible(self.NEW_ACCOUNT_NUMBER_LINK)

    def get_account_opened_heading_text(self) -> str:
        return self.get_text(self.ACCOUNT_OPENED_HEADING)

    def is_new_account_number_visible(self) -> bool:
        return self.is_visible(self.NEW_ACCOUNT_NUMBER_LINK)

    def get_new_account_number(self) -> str:
        return self.get_text(self.NEW_ACCOUNT_NUMBER_LINK)

    def _select_first_valid_option(self, dropdown: Locator) -> str | None:
        options = dropdown.locator("option")
        count = options.count()

        for index in range(count):
            option = options.nth(index)
            value = (option.get_attribute("value") or "").strip()
            text = option.inner_text().strip()

            if value and text:
                dropdown.select_option(
                    value=value,
                    timeout=self.config_manager.get_playwright_action_timeout_millis(),
                )
                self.logger.info("Selected dropdown option. Value=%s | Text=%s", value, text)
                return value

        return None