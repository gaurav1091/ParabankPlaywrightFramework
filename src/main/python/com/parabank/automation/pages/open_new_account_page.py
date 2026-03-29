from __future__ import annotations

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from com.parabank.automation.base.base_page import BasePage


class OpenNewAccountPage(BasePage):
    PAGE_HEADING = "css=div#openAccountForm h1.title"
    ACCOUNT_TYPE_DROPDOWN = "#type"
    FROM_ACCOUNT_DROPDOWN = "#fromAccountId"
    OPEN_NEW_ACCOUNT_BUTTON = "input[value='Open New Account']"

    ACCOUNT_OPENED_HEADING = "css=div#openAccountResult h1.title"
    NEW_ACCOUNT_NUMBER_LINK = "#newAccountId"

    RIGHT_PANEL_ERRORS = "#rightPanel .error"
    RIGHT_PANEL_PARAGRAPHS = "#rightPanel p"
    OPEN_ACCOUNT_RESULT_PANEL = "#openAccountResult"

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

    def wait_for_account_creation_result(self, timeout_millis: int | None = None) -> "OpenNewAccountPage":
        effective_timeout = timeout_millis or self.config_manager.get_playwright_navigation_timeout_millis()

        candidate_locators = (
            self.ACCOUNT_OPENED_HEADING,
            self.NEW_ACCOUNT_NUMBER_LINK,
            self.OPEN_ACCOUNT_RESULT_PANEL,
            self.RIGHT_PANEL_ERRORS,
        )

        for selector in candidate_locators:
            try:
                self.page.locator(selector).first.wait_for(state="visible", timeout=effective_timeout)
                self.logger.info(
                    "Detected Open New Account result state using selector: %s",
                    selector,
                )
                return self
            except PlaywrightTimeoutError:
                continue
            except Exception as exc:
                self.logger.warning(
                    "Ignoring non-fatal exception while waiting for Open New Account result selector=%s | Error=%s",
                    selector,
                    exc,
                )
                continue

        self.logger.info(
            "No explicit Open New Account result selector became visible within timeout=%s ms. "
            "Continuing with page-content-based validation.",
            effective_timeout,
        )
        return self

    def click_open_new_account_button(self) -> "OpenNewAccountPage":
        self.logger.info("Clicking Open New Account button.")
        self.click(self.OPEN_NEW_ACCOUNT_BUTTON)
        self.wait_for_page_ready()
        self.wait_for_account_creation_result()
        return self

    def submit_open_new_account(self) -> "OpenNewAccountPage":
        return self.click_open_new_account_button()

    def open_new_account(self, account_type: str) -> "OpenNewAccountPage":
        self.logger.info("Opening new account with type: %s", account_type)
        return self.select_account_type(account_type).select_first_available_from_account().submit_open_new_account()

    def open_new_account_from_specific_source(self, account_type: str, from_account: str) -> "OpenNewAccountPage":
        self.logger.info(
            "Opening new account with type=%s using specific source account=%s",
            account_type,
            from_account,
        )
        return self.select_account_type(account_type).select_from_account(from_account).submit_open_new_account()

    def has_numeric_new_account_number(self) -> bool:
        if not self.is_new_account_number_visible():
            return False

        new_account_number = self.get_new_account_number()
        return new_account_number.isdigit()

    def is_account_creation_successful(self) -> bool:
        feedback_message = self.get_submission_feedback_message().lower()

        if self.has_numeric_new_account_number():
            return True

        if self.is_visible(self.ACCOUNT_OPENED_HEADING) and self.shows_success_text():
            return True

        return (
            "account opened" in feedback_message
            or "your account is now open" in feedback_message
            or "your new account number" in feedback_message
        )

    def get_account_opened_heading_text(self) -> str:
        return self.get_text(self.ACCOUNT_OPENED_HEADING)

    def is_new_account_number_visible(self) -> bool:
        return self.is_visible(self.NEW_ACCOUNT_NUMBER_LINK)

    def get_new_account_number(self) -> str:
        return self.get_text(self.NEW_ACCOUNT_NUMBER_LINK).strip()

    def get_submission_feedback_message(self) -> str:
        messages: list[str] = []

        selectors_to_try = [
            self.RIGHT_PANEL_ERRORS,
            self.OPEN_ACCOUNT_RESULT_PANEL,
            self.RIGHT_PANEL_PARAGRAPHS,
        ]

        for selector in selectors_to_try:
            try:
                locator = self.page.locator(selector)
                count = locator.count()

                for index in range(count):
                    text = locator.nth(index).inner_text().strip()
                    if text:
                        collapsed_text = " ".join(text.split())
                        if collapsed_text not in messages:
                            messages.append(collapsed_text)
            except Exception:
                continue

        if messages:
            combined_message = " | ".join(messages)
            self.logger.info("Open New Account submission feedback: %s", combined_message)
            return combined_message

        return "No visible submission feedback was found on the page."

    def shows_success_text(self) -> bool:
        feedback_message = self.get_submission_feedback_message().lower()
        return (
            "account opened" in feedback_message
            or "your account is now open" in feedback_message
            or "your new account number" in feedback_message
        )
