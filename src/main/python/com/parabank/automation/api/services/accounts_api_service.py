from __future__ import annotations

from playwright.sync_api import Playwright

from com.parabank.automation.api.client.api_client import ApiClient
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class AccountsApiService:
    def __init__(self, playwright: Playwright, config_manager: ConfigManager) -> None:
        self._logger = FrameworkLogger.get_logger("parabank_framework.accounts_api_service")
        self._api_client = ApiClient(playwright, config_manager)

    def get_accounts_by_customer_id(self, customer_id: int, cookie_header: str) -> list[int]:
        self._logger.info("Fetching customer accounts via API. CustomerId=%s", customer_id)

        response = self._api_client.get_with_headers(
            f"customers/{customer_id}/accounts",
            headers={
                "Accept": "application/json",
                "Cookie": cookie_header,
            },
        )

        if not isinstance(response, list):
            raise AssertionError(
                f"Expected account list response for customerId={customer_id}, but got: {type(response).__name__}"
            )

        account_ids: list[int] = []

        for account in response:
            if not isinstance(account, dict):
                continue

            account_id = account.get("id")
            if account_id is not None:
                account_ids.append(int(account_id))

        return account_ids

    def dispose(self) -> None:
        self._api_client.dispose()