from __future__ import annotations

from playwright.sync_api import Playwright

from com.parabank.automation.api.client.api_client import ApiClient
from com.parabank.automation.api.endpoints.api_routes import ApiRoutes
from com.parabank.automation.api.models.api_response import ApiResponse
from com.parabank.automation.api.models.customer_account_summary import CustomerAccountSummary
from com.parabank.automation.assertions.api_assertions import ApiAssertions
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class AccountsApiService:
    def __init__(self, playwright: Playwright, config_manager: ConfigManager) -> None:
        self._logger = FrameworkLogger.get_logger("parabank_framework.accounts_api_service")
        self._api_client = ApiClient(playwright, config_manager)

    def get_accounts_response_by_customer_id(
        self,
        customer_id: int,
        cookie_header: str | None = None,
    ) -> ApiResponse:
        self._logger.info("Fetching customer accounts via API. CustomerId=%s", customer_id)

        headers: dict[str, str] = {
            "Accept": "application/json",
        }

        if cookie_header:
            headers["Cookie"] = cookie_header

        return self._api_client.get(
            ApiRoutes.customer_accounts(customer_id),
            headers=headers,
        )

    def get_accounts_payload_by_customer_id(
        self,
        customer_id: int,
        cookie_header: str | None = None,
    ) -> list[dict]:
        response = self.get_accounts_response_by_customer_id(customer_id, cookie_header)

        ApiAssertions.assert_status_code(
            response.status_code,
            200,
            f"Accounts API status code mismatch for customerId={customer_id}.",
        )
        ApiAssertions.assert_response_is_list(
            response.json_payload,
            f"Expected account list response for customerId={customer_id}.",
        )
        ApiAssertions.assert_list_not_empty(
            response.json_payload,
            f"Account list response should not be empty for customerId={customer_id}.",
        )
        ApiAssertions.assert_all_accounts_have_valid_core_fields(
            response.json_payload,
            f"Account payload validation failed for customerId={customer_id}.",
        )

        return response.json_payload

    def get_account_summaries_by_customer_id(
        self,
        customer_id: int,
        cookie_header: str | None = None,
    ) -> list[CustomerAccountSummary]:
        payload = self.get_accounts_payload_by_customer_id(customer_id, cookie_header)
        return [CustomerAccountSummary.from_dict(item) for item in payload]

    def get_accounts_by_customer_id(
        self,
        customer_id: int,
        cookie_header: str | None = None,
    ) -> list[str]:
        account_summaries = self.get_account_summaries_by_customer_id(customer_id, cookie_header)
        account_ids = [str(summary.account_id) for summary in account_summaries]

        self._logger.info(
            "API account IDs normalized to string. Count=%s | Sample=%s",
            len(account_ids),
            account_ids[:3],
        )

        return account_ids

    def dispose(self) -> None:
        self._api_client.dispose()
