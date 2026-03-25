import pytest
from playwright.sync_api import Page

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.assertions.ui_assertions import UiAssertions
from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.pages.admin_page import AdminPage


pytestmark = [pytest.mark.ui, pytest.mark.api, pytest.mark.hybrid, pytest.mark.integration, pytest.mark.regression]


def test_environment_hybrid_readiness_is_detected_correctly(
    framework_page: Page,
    framework_config: ConfigManager,
) -> None:
    admin_page = AdminPage(framework_page, framework_config)
    admin_page.open_admin_page()

    UiAssertions.assert_element_visible(
        framework_page,
        admin_page.is_administration_heading_visible(),
        "Administration Heading",
        "Administration heading should be visible on admin page.",
        "phase13_admin_heading_visibility",
    )

    CommonAssertions.assert_true(
        admin_page.is_data_access_mode_section_visible(),
        "Data Access Mode section should be detectable on admin page.",
    )

    readiness = admin_page.get_environment_readiness()

    CommonAssertions.assert_not_none(
        readiness,
        "Environment readiness should be created from admin page.",
    )
    CommonAssertions.assert_not_equals(
        readiness.selected_data_access_mode,
        "UNKNOWN",
        "Environment data access mode should be resolved from admin page.",
    )

    allowed_modes = ["SOAP", "REST (XML)", "REST (JSON)", "JDBC"]
    CommonAssertions.assert_contains(
        allowed_modes,
        readiness.selected_data_access_mode,
        "Resolved data access mode should be one of the supported admin page modes.",
    )

    if readiness.selected_data_access_mode == "JDBC":
        CommonAssertions.assert_false(
            readiness.rest_hybrid_supported,
            "REST hybrid support should be disabled for JDBC mode.",
        )
        CommonAssertions.assert_contains(
            readiness.reason,
            "JDBC",
            "Readiness reason should mention JDBC mode.",
        )

    elif readiness.selected_data_access_mode == "REST (JSON)":
        CommonAssertions.assert_true(
            readiness.rest_hybrid_supported,
            "REST hybrid support should be enabled for REST (JSON) mode.",
        )
        CommonAssertions.assert_contains(
            readiness.reason,
            "REST (JSON)",
            "Readiness reason should mention REST (JSON) mode.",
        )

    else:
        CommonAssertions.assert_false(
            readiness.rest_hybrid_supported,
            "REST hybrid support should remain disabled for non-REST(JSON) modes.",
        )