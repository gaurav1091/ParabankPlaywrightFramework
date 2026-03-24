from com.parabank.automation.base.base_page import BasePage


class AccountsOverviewPage(BasePage):
    PAGE_HEADING = "xpath=//h1[normalize-space()='Accounts Overview']"
    ACCOUNTS_TABLE = "#accountTable"
    ACCOUNT_ROWS = "#accountTable tbody tr"
    ACCOUNT_LINKS = "#accountTable tbody tr td a"

    def is_page_heading_visible(self) -> bool:
        return self.is_visible(self.PAGE_HEADING)

    def get_page_heading_text(self) -> str:
        return self.get_text(self.PAGE_HEADING)

    def is_accounts_table_visible(self) -> bool:
        return self.is_visible(self.ACCOUNTS_TABLE)

    def get_account_row_count(self) -> int:
        return self.get_count(self.ACCOUNT_ROWS)

    def get_account_link_count(self) -> int:
        return self.get_count(self.ACCOUNT_LINKS)