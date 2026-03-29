from __future__ import annotations

from com.parabank.automation.base.base_page import BasePage
from com.parabank.automation.utils.wait_utils import WaitUtils


class LoginPage(BasePage):
    USERNAME_INPUT = "input[name='username']"
    PASSWORD_INPUT = "input[name='password']"
    LOGIN_BUTTON = "input[value='Log In']"
    FORGOT_LOGIN_INFO_LINK = "text=Forgot login info?"
    REGISTER_LINK = "text=Register"
    ERROR_MESSAGE = "#rightPanel .error"

    def open_login_page(self) -> None:
        self.logger.info("Opening login page.")
        self.open_base_url()
        self.wait_for_page_ready()

    def is_login_page_displayed(self) -> bool:
        return self.is_username_field_visible() and self.is_password_field_visible() and self.is_login_button_visible()

    def is_username_field_visible(self) -> bool:
        return self.is_visible(self.USERNAME_INPUT)

    def is_password_field_visible(self) -> bool:
        return self.is_visible(self.PASSWORD_INPUT)

    def is_login_button_visible(self) -> bool:
        return self.is_visible(self.LOGIN_BUTTON)

    def enter_username(self, username: str) -> None:
        self.logger.info("Entering username on login page.")
        self.enter_text(self.USERNAME_INPUT, username)

    def enter_password(self, password: str) -> None:
        self.logger.info("Entering password on login page.")
        self.enter_text(self.PASSWORD_INPUT, password)

    def click_login(self) -> None:
        self.logger.info("Clicking login button.")
        self.click(self.LOGIN_BUTTON)
        WaitUtils.wait_for_page_load(self.page, self.config_manager)
        self.wait_for_page_ready()

    def login(self, username: str, password: str) -> "HomePage":
        self.logger.info("Performing login flow.")
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

        from com.parabank.automation.pages.home_page import HomePage

        return HomePage(self.page, self.config_manager)

    def login_expecting_failure(self, username: str, password: str) -> "LoginPage":
        self.logger.info("Performing login flow expecting failure.")
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        return self

    def get_error_message(self) -> str:
        return self.get_text(self.ERROR_MESSAGE)

    def is_error_message_visible(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)
