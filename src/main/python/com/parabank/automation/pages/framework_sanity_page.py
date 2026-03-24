from com.parabank.automation.base.base_page import BasePage


class FrameworkSanityPage(BasePage):
    LOGO = "img[title='ParaBank']"
    WELCOME_PANEL = "#leftPanel"
    CUSTOMER_LOGIN_TITLE = "text=Customer Login"

    def open_application(self) -> None:
        self.open_base_url()

    def is_logo_visible(self) -> bool:
        return self.is_visible(self.LOGO)

    def is_left_panel_visible(self) -> bool:
        return self.is_visible(self.WELCOME_PANEL)

    def is_customer_login_title_visible(self) -> bool:
        return self.is_visible(self.CUSTOMER_LOGIN_TITLE)