import pytest
from playwright.sync_api import Playwright

from com.parabank.automation.api.client.api_client import ApiClient
from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.config.config_manager import ConfigManager

pytestmark = [pytest.mark.api, pytest.mark.sanity]


def test_api_client_can_be_initialized_and_disposed(
    framework_playwright: Playwright,
    framework_config: ConfigManager,
) -> None:
    client = ApiClient(framework_playwright, framework_config)

    try:
        CommonAssertions.assert_not_none(
            client,
            "API client should be initialized successfully.",
        )
    finally:
        client.dispose()
