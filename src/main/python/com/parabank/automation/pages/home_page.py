from __future__ import annotations

from typing import TYPE_CHECKING

from com.parabank.automation.base.base_page import BasePage

if TYPE_CHECKING:
    from com.parabank.automation.pages.accounts_overview_page import AccountsOverviewPage
    from com.parabank.automation.pages.bill_pay_page import BillPayPage
    from com.parabank.automation.pages.find_transactions_page import FindTransactionsPage
    from com.parabank.automation.pages.login_page import LoginPage
    from com.parabank.automation.pages.open_new_account_page import OpenNewAccountPage
    from com.parabank.automation.pages.transfer_funds_page import TransferFundsPage


class HomePage(BasePage):
    ACCOUNTS_OVERVIEW_LINK = "#leftPanel a[href*='overview.htm']"
    OPEN_NEW_ACCOUNT_LINK = "#leftPanel a[href*='openaccount.htm']"
    TRANSFER_FUNDS_LINK = "#leftPanel a[href*='transfer.htm']"
    BILL_PAY_LINK = "#leftPanel a[href*='billpay.htm']"
    FIND_TRANSACTIONS_LINK = "#leftPanel a[href*='findtrans.htm']"
    LOG_OUT_LINK = "#leftPanel a[href*='logout.htm']"
    LEFT_PANEL = "#leftPanel"

    def is_left_panel_visible(self) -> bool:
        return self.is_visible(self.LEFT_PANEL)

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

    def is_home_page_loaded(self) -> bool:
        return (
            self.is_left_panel_visible()
            and self.is_logout_link_visible()
            and self.is_accounts_overview_link_visible()
            and self.is_open_new_account_link_visible()
            and self.is_transfer_funds_link_visible()
            and self.is_bill_pay_link_visible()
            and self.is_find_transactions_link_visible()
        )

    def go_to_accounts_overview(self) -> AccountsOverviewPage:
        self.logger.info("Navigating to Accounts Overview page.")
        self.click(self.ACCOUNTS_OVERVIEW_LINK)
        self.wait_for_url_contains("overview")
        self.wait_for_page_ready()

        from com.parabank.automation.pages.accounts_overview_page import AccountsOverviewPage

        return AccountsOverviewPage(self.page, self.config_manager)

    def go_to_open_new_account(self) -> OpenNewAccountPage:
        self.logger.info("Navigating to Open New Account page.")
        self.click(self.OPEN_NEW_ACCOUNT_LINK)
        self.wait_for_url_contains("openaccount")
        self.wait_for_page_ready()

        from com.parabank.automation.pages.open_new_account_page import OpenNewAccountPage

        return OpenNewAccountPage(self.page, self.config_manager)

    def go_to_transfer_funds(self) -> TransferFundsPage:
        self.logger.info("Navigating to Transfer Funds page.")
        self.click(self.TRANSFER_FUNDS_LINK)
        self.wait_for_url_contains("transfer")
        self.wait_for_page_ready()

        from com.parabank.automation.pages.transfer_funds_page import TransferFundsPage

        return TransferFundsPage(self.page, self.config_manager)

    def go_to_bill_pay(self) -> BillPayPage:
        self.logger.info("Navigating to Bill Pay page.")
        self.click(self.BILL_PAY_LINK)
        self.wait_for_url_contains("billpay")
        self.wait_for_page_ready()

        from com.parabank.automation.pages.bill_pay_page import BillPayPage

        return BillPayPage(self.page, self.config_manager)

    def go_to_find_transactions(self) -> FindTransactionsPage:
        self.logger.info("Navigating to Find Transactions page.")
        self.click(self.FIND_TRANSACTIONS_LINK)
        self.wait_for_url_contains("findtrans")
        self.wait_for_page_ready()

        from com.parabank.automation.pages.find_transactions_page import FindTransactionsPage

        return FindTransactionsPage(self.page, self.config_manager)

    def logout(self) -> LoginPage:
        self.logger.info("Logging out from application.")
        self.click(self.LOG_OUT_LINK)
        self.wait_for_url_contains("index")
        self.wait_for_page_ready()

        from com.parabank.automation.pages.login_page import LoginPage

        return LoginPage(self.page, self.config_manager)
