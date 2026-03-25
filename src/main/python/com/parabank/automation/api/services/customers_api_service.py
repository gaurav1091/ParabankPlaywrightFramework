from playwright.sync_api import Playwright

from com.parabank.automation.api.client.api_client import ApiClient
from com.parabank.automation.api.models.customer_account_summary import CustomerAccountSummary
from com.parabank.automation.api.models.customer_summary import CustomerSummary
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class CustomersApiService:
    def __init__(self, playwright: Playwright, config_manager: ConfigManager) -> None:
        self._logger = FrameworkLogger.get_logger("parabank_framework.customers_api_service")
        self._api_client = ApiClient(playwright, config_manager)

    def login_and_get_customer(self, username: str, password: str) -> CustomerSummary:
        self._logger.info("Logging in through API for customer lookup. Username=%s", username)
        payload = self._api_client.get_json_object(f"/login/{username}/{password}")
        return CustomerSummary.from_dict(payload)

    def get_customer_accounts(self, customer_id: int) -> list[CustomerAccountSummary]:
        self._logger.info("Fetching customer accounts via API. CustomerId=%s", customer_id)
        payload = self._api_client.get_json_array(f"/customers/{customer_id}/accounts")
        return [CustomerAccountSummary.from_dict(item) for item in payload]

    def dispose(self) -> None:
        self._api_client.dispose()