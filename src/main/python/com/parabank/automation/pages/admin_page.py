from __future__ import annotations

from typing import Any

from com.parabank.automation.base.base_page import BasePage
from com.parabank.automation.models.environment_readiness import EnvironmentReadiness
from com.parabank.automation.utils.wait_utils import WaitUtils


class AdminPage(BasePage):
    ADMIN_PAGE_PATH = "/admin.htm"
    ADMINISTRATION_HEADING = "xpath=//h1[normalize-space()='Administration']"
    DATA_ACCESS_MODE_HEADING = "xpath=//*[normalize-space()='Data Access Mode']"
    REST_ENDPOINT_LABEL = "xpath=//*[contains(normalize-space(),'REST Endpoint')]"

    def open_admin_page(self) -> None:
        self.logger.info("Opening admin page.")
        self.open(f"{self.config_manager.get_base_url().rstrip('/')}{self.ADMIN_PAGE_PATH}")
        WaitUtils.wait_for_page_load(self.page, self.config_manager)

    def is_administration_heading_visible(self) -> bool:
        return self.is_visible(self.ADMINISTRATION_HEADING)

    def is_data_access_mode_section_visible(self) -> bool:
        selectors = [
            self.DATA_ACCESS_MODE_HEADING,
            "xpath=//h3[normalize-space()='Data Access Mode']",
            "xpath=//*[contains(normalize-space(),'Data Access Mode')]",
        ]

        for selector in selectors:
            try:
                if self.is_visible(selector):
                    return True
            except Exception:
                continue

        page_text = self.page.locator("body").inner_text()
        return "Data Access Mode" in page_text

    def get_rest_endpoint_value(self) -> str:
        selectors = [
            "xpath=//*[normalize-space()='REST Endpoint:']/following::input[1]",
            "xpath=//*[contains(normalize-space(),'REST Endpoint')]/following::input[1]",
            "xpath=//label[contains(normalize-space(),'REST Endpoint')]/following::input[1]",
        ]

        for selector in selectors:
            try:
                locator = self.page.locator(selector).first
                if locator.count() > 0:
                    return locator.input_value().strip()
            except Exception:
                continue

        return ""

    def get_selected_data_access_mode(self) -> str:
        selected_radios: list[dict[str, Any]] = self.page.evaluate(
            """
            () => {
                return Array.from(document.querySelectorAll('input[type="radio"]:checked')).map(r => ({
                    value: r.value || '',
                    id: r.id || '',
                    name: r.name || '',
                    outerHTML: r.outerHTML || ''
                }));
            }
            """
        )

        for radio in selected_radios:
            normalized = " ".join(
                [
                    str(radio.get("value", "")),
                    str(radio.get("id", "")),
                    str(radio.get("name", "")),
                    str(radio.get("outerHTML", "")),
                ]
            ).lower()

            if "jdbc" in normalized:
                return "JDBC"
            if "rest" in normalized and "json" in normalized:
                return "REST (JSON)"
            if "rest" in normalized and "xml" in normalized:
                return "REST (XML)"
            if "soap" in normalized:
                return "SOAP"

        page_text = self.page.locator("body").inner_text()

        if "JDBC*" in page_text or "\nJDBC" in page_text:
            return "JDBC"
        if "REST (JSON)" in page_text or "REST JSON" in page_text:
            return "REST (JSON)"
        if "REST (XML)" in page_text or "REST XML" in page_text:
            return "REST (XML)"
        if "\nSOAP" in page_text or page_text.strip().startswith("SOAP"):
            return "SOAP"

        return "UNKNOWN"

    def get_environment_readiness(self) -> EnvironmentReadiness:
        mode = self.get_selected_data_access_mode()
        rest_endpoint_value = self.get_rest_endpoint_value()

        if mode == "REST (JSON)":
            return EnvironmentReadiness(
                selected_data_access_mode=mode,
                rest_endpoint_value=rest_endpoint_value,
                rest_hybrid_supported=True,
                reason="Environment is configured for REST (JSON). Hybrid REST validation is supported.",
            )

        if mode == "REST (XML)":
            return EnvironmentReadiness(
                selected_data_access_mode=mode,
                rest_endpoint_value=rest_endpoint_value,
                rest_hybrid_supported=False,
                reason="Environment is configured for REST (XML). JSON-style hybrid validation is not supported.",
            )

        if mode == "SOAP":
            return EnvironmentReadiness(
                selected_data_access_mode=mode,
                rest_endpoint_value=rest_endpoint_value,
                rest_hybrid_supported=False,
                reason="Environment is configured for SOAP. REST hybrid validation is not supported.",
            )

        if mode == "JDBC":
            return EnvironmentReadiness(
                selected_data_access_mode=mode,
                rest_endpoint_value=rest_endpoint_value,
                rest_hybrid_supported=False,
                reason="Environment is configured for JDBC. REST hybrid validation is intentionally not attempted.",
            )

        return EnvironmentReadiness(
            selected_data_access_mode=mode,
            rest_endpoint_value=rest_endpoint_value,
            rest_hybrid_supported=False,
            reason="Environment data access mode could not be resolved reliably from the admin page.",
        )