from com.parabank.automation.base.base_page import BasePage
from com.parabank.automation.utils.wait_utils import WaitUtils


class HomePage(BasePage):
    ACCOUNTS_OVERVIEW_LINK = "#leftPanel a[href*='overview.htm']"
    OPEN_NEW_ACCOUNT_LINK = "#leftPanel a[href*='openaccount.htm']"
    TRANSFER_FUNDS_LINK = "#leftPanel a[href*='transfer.htm']"
    BILL_PAY_LINK = "#leftPanel a[href*='billpay.htm']"
    FIND_TRANSACTIONS_LINK = "#leftPanel a[href*='findtrans.htm']"
    LOG_OUT_LINK = "#leftPanel a[href*='logout.htm']"
    WELCOME_PANEL = "#leftPanel"

    def is_logout_link_visible(self) -> bool:
        return self.is_visible(self.LOG_OUT_LINK)

    def is_accounts_overview_link_visible(self) -> bool:
        return self.is_visible(self.ACCOUNTS_OVERVIEW_LINK)

    def is_open_new_account_link_visible(self) -> bool:
        return self.is_visible(self.OPEN_NEW_ACCOUNT_LINK)

    def is_transfer_funds_link_visible(self) -> bool:
        return self.is_visible(self.TRANSFER_FUNDS_LINK)

    def is_bill_pay_link_visible(self) -> bool:
        return self.is_visible(self.BILL_PAY_LINK)

    def is_find_transactions_link_visible(self) -> bool:
        return self.is_visible(self.FIND_TRANSACTIONS_LINK)

    def is_left_panel_visible(self) -> bool:
        return self.is_visible(self.WELCOME_PANEL)

    def go_to_accounts_overview(self) -> "AccountsOverviewPage":
        self.logger.info("Navigating to Accounts Overview page.")
        self.click(self.ACCOUNTS_OVERVIEW_LINK)
        self.wait_for_url_contains("overview")
        WaitUtils.wait_for_page_load(self.page, self.config_manager)

        from com.parabank.automation.pages.accounts_overview_page import AccountsOverviewPage
        return AccountsOverviewPage(self.page, self.config_manager)