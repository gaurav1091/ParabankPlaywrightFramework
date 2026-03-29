from __future__ import annotations

from typing import Any

from playwright.sync_api import APIRequestContext, Playwright

from com.parabank.automation.api.models.api_response import ApiResponse
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class ApiClient:
    def __init__(self, playwright: Playwright, config_manager: ConfigManager) -> None:
        self._playwright = playwright
        self._config_manager = config_manager
        self._logger = FrameworkLogger.get_logger("parabank_framework.api_client")

        base_url = self._config_manager.get_api_base_url().rstrip("/") + "/"
        api_timeout_millis = self._config_manager.get_api_read_timeout_seconds() * 1000

        self._request_context: APIRequestContext = self._playwright.request.new_context(
            base_url=base_url,
            extra_http_headers={
                "Accept": "application/json",
            },
            ignore_https_errors=self._config_manager.is_playwright_ignore_https_errors_enabled(),
            timeout=api_timeout_millis,
        )

    @staticmethod
    def _normalize_relative_path(path: str) -> str:
        if path is None:
            raise ValueError("API path cannot be None.")

        normalized_path = str(path).strip()

        if not normalized_path:
            raise ValueError("API path cannot be blank.")

        return normalized_path.lstrip("/")

    def get(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> ApiResponse:
        normalized_path = self._normalize_relative_path(path)
        effective_headers = headers or {}

        self._logger.info(
            "Sending API GET request. RelativePath=%s | Headers=%s",
            normalized_path,
            sorted(effective_headers.keys()),
        )

        response = self._request_context.get(normalized_path, headers=effective_headers or None)
        body_text = response.text()

        try:
            json_payload: Any = response.json()
        except Exception:
            json_payload = None

        response_headers = response.headers
        if callable(response_headers):
            response_headers = response.headers()

        api_response = ApiResponse(
            status_code=response.status,
            ok=response.ok,
            headers=dict(response_headers),
            body_text=body_text,
            json_payload=json_payload,
        )

        self._logger.info(
            "Received API response. RelativePath=%s | Status=%s | OK=%s | BodyLength=%s",
            normalized_path,
            api_response.status_code,
            api_response.ok,
            len(api_response.body_text),
        )

        return api_response

    def get_json_object(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        normalized_path = self._normalize_relative_path(path)
        response = self.get(normalized_path, headers=headers)

        if not response.ok:
            raise AssertionError(
                f"GET request failed. Path={normalized_path} | Status={response.status_code} | Body={response.body_text}"
            )

        if not isinstance(response.json_payload, dict):
            raise AssertionError(
                f"Expected JSON object response. Path={normalized_path} | Status={response.status_code} | "
                f"ActualType={type(response.json_payload)!r}"
            )

        return response.json_payload

    def get_json_array(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        normalized_path = self._normalize_relative_path(path)
        response = self.get(normalized_path, headers=headers)

        if not response.ok:
            raise AssertionError(
                f"GET request failed. Path={normalized_path} | Status={response.status_code} | Body={response.body_text}"
            )

        if not isinstance(response.json_payload, list):
            raise AssertionError(
                f"Expected JSON array response. Path={normalized_path} | Status={response.status_code} | "
                f"ActualType={type(response.json_payload)!r}"
            )

        return response.json_payload

    def dispose(self) -> None:
        self._logger.info("Closing API request context.")
        self._request_context.dispose()