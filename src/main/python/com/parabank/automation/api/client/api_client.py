from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext, Playwright

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class ApiClient:
    def __init__(self, playwright: Playwright, config_manager: ConfigManager) -> None:
        self._playwright = playwright
        self._config_manager = config_manager
        self._logger = FrameworkLogger.get_logger("parabank_framework.api_client")

        self._request_context: APIRequestContext = self._playwright.request.new_context(
            base_url=self._config_manager.get_api_base_url(),
            extra_http_headers={
                "Accept": "application/json",
            },
            ignore_https_errors=self._config_manager.is_playwright_ignore_https_errors_enabled(),
        )

    def get(self, path: str) -> Any:
        self._logger.info("Sending API GET request. Path=%s", path)

        response = self._request_context.get(path)

        self._logger.info(
            "Received API response. Path=%s | Status=%s | OK=%s",
            path,
            response.status,
            response.ok,
        )

        if not response.ok:
            raise AssertionError(
                f"GET request failed. Path={path} | Status={response.status} | Body={response.text()}"
            )

        try:
            return response.json()
        except Exception as exc:
            raise AssertionError(
                f"Response body is not valid JSON. Path={path} | Status={response.status}"
            ) from exc

    def get_json_object(self, path: str) -> dict[str, Any]:
        payload = self.get(path)

        if not isinstance(payload, dict):
            raise AssertionError(
                f"Expected JSON object response. Path={path} | ActualType={type(payload).__name__}"
            )

        return payload

    def get_json_array(self, path: str) -> list[dict[str, Any]]:
        payload = self.get(path)

        if not isinstance(payload, list):
            raise AssertionError(
                f"Expected JSON array response. Path={path} | ActualType={type(payload).__name__}"
            )

        normalized: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                raise AssertionError(
                    f"Expected JSON object items in array response. Path={path} | ItemType={type(item).__name__}"
                )
            normalized.append(item)

        return normalized

    def dispose(self) -> None:
        self._logger.info("Closing API request context.")
        self._request_context.dispose()