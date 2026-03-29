from com.parabank.automation.api.services.accounts_api_service import AccountsApiService
from com.parabank.automation.assertions.api_assertions import ApiAssertions
from com.parabank.automation.context.framework_context import FrameworkContext
from com.parabank.automation.pages.accounts_overview_page import AccountsOverviewPage
from com.parabank.automation.utils.cookie_utils import CookieUtils
from com.parabank.automation.utils.customer_utils import CustomerUtils
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class HybridAccountsService:
    def __init__(
        self,
        accounts_overview_page: AccountsOverviewPage,
        api_service: AccountsApiService,
    ) -> None:
        self._accounts_overview_page = accounts_overview_page
        self._api_service = api_service
        self._logger = FrameworkLogger.get_logger("parabank_framework.hybrid_accounts_service")

    def load_ui_data(self, context: FrameworkContext) -> None:
        context.ui_account_ids = self._accounts_overview_page.get_account_numbers()

        page_source = self._accounts_overview_page.page.content()
        context.customer_id = CustomerUtils.extract_customer_id_from_page_source(page_source)

        cookies = self._accounts_overview_page.page.context.cookies()
        context.cookie_header = CookieUtils.build_cookie_header(cookies)

        self._logger.info(
            "Hybrid UI data loaded successfully. CustomerId=%s | UIAccountCount=%s",
            context.customer_id,
            len(context.ui_account_ids),
        )

    def load_api_data(self, context: FrameworkContext) -> None:
        if context.customer_id is None:
            raise AssertionError("Customer ID is not available in framework context.")

        if not context.cookie_header:
            raise AssertionError("Cookie header is not available in framework context.")

        context.api_account_ids = self._api_service.get_accounts_by_customer_id(
            context.customer_id,
            context.cookie_header,
        )

        self._logger.info(
            "Hybrid API data loaded successfully. APIAccountCount=%s",
            len(context.api_account_ids),
        )

    def validate_ui_vs_api(self, context: FrameworkContext) -> None:
        ApiAssertions.assert_list_not_empty(
            context.ui_account_ids,
            "UI account list should not be empty.",
        )
        ApiAssertions.assert_list_not_empty(
            context.api_account_ids,
            "API account list should not be empty.",
        )
        ApiAssertions.assert_collections_match_ignoring_order(
            context.ui_account_ids,
            context.api_account_ids,
            "Mismatch between UI and API account ids.",
        )

        self._logger.info("Hybrid validation passed successfully. UI and API accounts match.")
