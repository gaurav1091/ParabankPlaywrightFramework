from playwright.sync_api import Playwright

from com.parabank.automation.api.client.api_client import ApiClient
from com.parabank.automation.api.models.account_details import AccountDetails
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class AccountsApiService:
    def __init__(self, playwright: Playwright, config_manager: ConfigManager) -> None:
        self._logger = FrameworkLogger.get_logger("parabank_framework.accounts_api_service")
        self._api_client = ApiClient(playwright, config_manager)

    def get_account_details(self, account_id: int) -> AccountDetails:
        self._logger.info("Fetching account details via API. AccountId=%s", account_id)
        payload = self._api_client.get_json(f"/accounts/{account_id}")
        return AccountDetails.from_dict(payload)

    def dispose(self) -> None:
        self._api_client.dispose()