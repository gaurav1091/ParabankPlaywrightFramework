from playwright.sync_api import Locator

from com.parabank.automation.base.base_page import BasePage
from com.parabank.automation.utils.wait_utils import WaitUtils


class TransferFundsPage(BasePage):
    PAGE_HEADING = "xpath=//h1[normalize-space()='Transfer Funds']"
    AMOUNT_INPUT = "#amount"
    FROM_ACCOUNT_DROPDOWN = "#fromAccountId"
    TO_ACCOUNT_DROPDOWN = "#toAccountId"
    TRANSFER_BUTTON = "input[value='Transfer']"

    TRANSFER_COMPLETE_HEADING = "xpath=//h1[normalize-space()='Transfer Complete!']"
    TRANSFER_RESULT_MESSAGE = "#showResult p"
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
        self.enter_text(self.AMOUNT_INPUT, amount)
        return self

    def select_first_available_accounts(self) -> "TransferFundsPage":
        self.logger.info("Selecting source and destination accounts for transfer.")

        from_dropdown = self.page.locator(self.FROM_ACCOUNT_DROPDOWN)
        to_dropdown = self.page.locator(self.TO_ACCOUNT_DROPDOWN)

        from_dropdown.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        to_dropdown.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )

        from_value = self._select_first_valid_option(from_dropdown)
        if from_value is None:
            raise RuntimeError("No valid source account available in transfer dropdown.")

        to_value = self._select_first_valid_option_excluding(to_dropdown, excluded_value=from_value)
        if to_value is None:
            to_value = self._select_first_valid_option(to_dropdown)

        if to_value is None:
            raise RuntimeError("No valid destination account available in transfer dropdown.")

        return self

    def get_selected_from_account(self) -> str:
        dropdown = self.page.locator(self.FROM_ACCOUNT_DROPDOWN)
        dropdown.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        selected_text = dropdown.locator("option:checked").inner_text().strip()
        self.logger.info("Selected from-account: %s", selected_text)
        return selected_text

    def get_selected_to_account(self) -> str:
        dropdown = self.page.locator(self.TO_ACCOUNT_DROPDOWN)
        dropdown.wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_action_timeout_millis(),
        )
        selected_text = dropdown.locator("option:checked").inner_text().strip()
        self.logger.info("Selected to-account: %s", selected_text)
        return selected_text

    def click_transfer_button(self) -> "TransferFundsPage":
        self.logger.info("Clicking Transfer button.")
        self.click(self.TRANSFER_BUTTON)
        self._wait_for_transfer_result()
        return self

    def transfer_funds(self, amount: str) -> "TransferFundsPage":
        self.logger.info("Executing transfer funds flow with amount: %s", amount)
        return self.enter_amount(amount).select_first_available_accounts().click_transfer_button()

    def is_transfer_successful(self) -> bool:
        self._wait_for_transfer_result()
        return self.is_visible(self.TRANSFER_COMPLETE_HEADING) and self.is_visible(self.TRANSFER_RESULT_MESSAGE)

    def get_transfer_complete_heading_text(self) -> str:
        self._wait_for_transfer_result()
        return self.get_text(self.TRANSFER_COMPLETE_HEADING)

    def get_transfer_result_message(self) -> str:
        self._wait_for_transfer_result()
        return self.get_text(self.TRANSFER_RESULT_MESSAGE)

    def get_transferred_amount_value(self) -> str:
        self._wait_for_transfer_result()
        return self.get_text(self.TRANSFERRED_AMOUNT_VALUE)

    def get_result_from_account_value(self) -> str:
        self._wait_for_transfer_result()
        return self.get_text(self.FROM_ACCOUNT_RESULT_VALUE)

    def get_result_to_account_value(self) -> str:
        self._wait_for_transfer_result()
        return self.get_text(self.TO_ACCOUNT_RESULT_VALUE)

    def _wait_for_transfer_result(self) -> None:
        WaitUtils.wait_for_page_load(self.page, self.config_manager)
        self.page.locator(self.TRANSFER_COMPLETE_HEADING).wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_navigation_timeout_millis(),
        )
        self.page.locator(self.TRANSFER_RESULT_MESSAGE).wait_for(
            state="visible",
            timeout=self.config_manager.get_playwright_navigation_timeout_millis(),
        )

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

    def _select_first_valid_option_excluding(self, dropdown: Locator, excluded_value: str) -> str | None:
        options = dropdown.locator("option")
        count = options.count()

        for index in range(count):
            option = options.nth(index)
            value = (option.get_attribute("value") or "").strip()
            text = option.inner_text().strip()

            if value and text and value != excluded_value:
                dropdown.select_option(
                    value=value,
                    timeout=self.config_manager.get_playwright_action_timeout_millis(),
                )
                self.logger.info(
                    "Selected dropdown option excluding source account. Value=%s | Text=%s",
                    value,
                    text,
                )
                return value

        return None