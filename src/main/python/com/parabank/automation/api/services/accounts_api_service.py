from __future__ import annotations

from playwright.sync_api import Playwright

from com.parabank.automation.api.client.api_client import ApiClient
from com.parabank.automation.assertions.api_assertions import ApiAssertions
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class AccountsApiService:
    def __init__(self, playwright: Playwright, config_manager: ConfigManager) -> None:
        self._logger = FrameworkLogger.get_logger("parabank_framework.accounts_api_service")
        self._api_client = ApiClient(playwright, config_manager)

    def get_accounts_by_customer_id(self, customer_id: int, cookie_header: str) -> list[str]:
        self._logger.info("Fetching customer accounts via API. CustomerId=%s", customer_id)

        response = self._api_client.get_with_headers(
            f"customers/{customer_id}/accounts",
            headers={
                "Accept": "application/json",
                "Cookie": cookie_header,
            },
        )

        # ✅ Assertions (unchanged)
        ApiAssertions.assert_response_is_list(
            response,
            f"Expected account list response for customerId={customer_id}.",
        )
        ApiAssertions.assert_list_not_empty(
            response,
            f"Account list response should not be empty for customerId={customer_id}.",
        )
        ApiAssertions.assert_all_accounts_have_valid_core_fields(
            response,
            f"Account payload validation failed for customerId={customer_id}.",
        )

        # ✅ FIX: Normalize to STRING (match UI layer)
        account_ids: list[str] = []

        for account in response:
            account_id = account.get("id")
            if account_id is not None:
                account_ids.append(str(account_id))   # 🔥 FIX HERE

        self._logger.info(
            "API account IDs normalized to string. Count=%s | Sample=%s",
            len(account_ids),
            account_ids[:3],
        )

        return account_ids

    def dispose(self) -> None:
        self._api_client.dispose()