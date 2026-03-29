from __future__ import annotations

from playwright.sync_api import Playwright

from com.parabank.automation.api.client.api_client import ApiClient
from com.parabank.automation.api.endpoints.api_routes import ApiRoutes
from com.parabank.automation.api.models.api_response import ApiResponse
from com.parabank.automation.api.models.customer_account_summary import CustomerAccountSummary
from com.parabank.automation.api.models.customer_summary import CustomerSummary
from com.parabank.automation.assertions.api_assertions import ApiAssertions
from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class CustomersApiService:
    def __init__(self, playwright: Playwright, config_manager: ConfigManager) -> None:
        self._logger = FrameworkLogger.get_logger("parabank_framework.customers_api_service")
        self._api_client = ApiClient(playwright, config_manager)

    def get_customer_response(self, customer_id: int) -> ApiResponse:
        self._logger.info("Fetching customer through API. CustomerId=%s", customer_id)
        return self._api_client.get(f"customers/{customer_id}")

    def get_customer(self, customer_id: int) -> CustomerSummary:
        response = self.get_customer_response(customer_id)

        ApiAssertions.assert_status_code(
            response.status_code,
            200,
            f"Customer API status code mismatch for customerId={customer_id}.",
        )
        ApiAssertions.assert_response_is_dict(
            response.json_payload,
            f"Expected customer response to be a JSON object for customerId={customer_id}.",
        )

        customer = CustomerSummary.from_dict(response.json_payload)

        CommonAssertions.assert_true(
            customer.customer_id > 0,
            f"Customer summary validation failed for customerId={customer_id}. Invalid customer_id.",
        )
        CommonAssertions.assert_not_empty(
            customer.username,
            f"Customer summary validation failed for customerId={customer_id}. Username is blank.",
        )

        return customer

    def get_customer_accounts_response(self, customer_id: int) -> ApiResponse:
        self._logger.info("Fetching customer accounts via API. CustomerId=%s", customer_id)
        return self._api_client.get(ApiRoutes.customer_accounts(customer_id))

    def get_customer_accounts(self, customer_id: int) -> list[CustomerAccountSummary]:
        response = self.get_customer_accounts_response(customer_id)

        ApiAssertions.assert_status_code(
            response.status_code,
            200,
            f"Customer accounts API status code mismatch for customerId={customer_id}.",
        )
        ApiAssertions.assert_response_is_list(
            response.json_payload,
            f"Expected customer accounts payload to be a JSON array for customerId={customer_id}.",
        )
        ApiAssertions.assert_all_accounts_have_valid_core_fields(
            response.json_payload,
            f"Customer account payload validation failed for customerId={customer_id}.",
        )

        return [CustomerAccountSummary.from_dict(item) for item in response.json_payload]

    def get_customer_account_ids(self, customer_id: int) -> list[str]:
        account_summaries = self.get_customer_accounts(customer_id)
        return [str(account_summary.account_id) for account_summary in account_summaries]

    def dispose(self) -> None:
        self._api_client.dispose()
