from playwright.sync_api import Page

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.utils.failure_diagnostics_utils import FailureDiagnosticsUtils
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class UiAssertions:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.ui_assertions")

    @classmethod
    def assert_page_title_contains(
        cls,
        page: Page,
        expected_partial_title: str,
        failure_message: str,
        diagnostic_name: str,
    ) -> None:
        actual_title = page.title()

        try:
            CommonAssertions.assert_contains(
                actual_title,
                expected_partial_title,
                failure_message,
            )
            cls.LOGGER.info(
                "UI assertion passed: page title contains expected value. ExpectedPartial=%s | ActualTitle=%s",
                expected_partial_title,
                actual_title,
            )
        except AssertionError as exc:
            diagnostics = FailureDiagnosticsUtils.capture_page_diagnostics(page, diagnostic_name)
            raise AssertionError(
                f"{failure_message} | Expected title to contain: {expected_partial_title!r} "
                f"| Actual title: {actual_title!r} "
                f"| Screenshot: {diagnostics['screenshot_path']} "
                f"| URL: {diagnostics['url']}"
            ) from exc

    @classmethod
    def assert_current_url_contains(
        cls,
        page: Page,
        expected_partial_url: str,
        failure_message: str,
        diagnostic_name: str,
    ) -> None:
        actual_url = page.url

        try:
            CommonAssertions.assert_contains(
                actual_url,
                expected_partial_url,
                failure_message,
            )
            cls.LOGGER.info(
                "UI assertion passed: current URL contains expected value. ExpectedPartial=%s | ActualURL=%s",
                expected_partial_url,
                actual_url,
            )
        except AssertionError as exc:
            diagnostics = FailureDiagnosticsUtils.capture_page_diagnostics(page, diagnostic_name)
            raise AssertionError(
                f"{failure_message} | Expected URL to contain: {expected_partial_url!r} "
                f"| Actual URL: {actual_url!r} "
                f"| Screenshot: {diagnostics['screenshot_path']} "
                f"| Title: {diagnostics['title']}"
            ) from exc

    @classmethod
    def assert_element_visible(
        cls,
        page: Page,
        actual_visible: bool,
        element_name: str,
        failure_message: str,
        diagnostic_name: str,
    ) -> None:
        try:
            CommonAssertions.assert_true(
                actual_visible,
                failure_message,
            )
            cls.LOGGER.info(
                "UI assertion passed: element is visible. ElementName=%s",
                element_name,
            )
        except AssertionError as exc:
            diagnostics = FailureDiagnosticsUtils.capture_page_diagnostics(page, diagnostic_name)
            raise AssertionError(
                f"{failure_message} | Element expected visible: {element_name!r} "
                f"| Screenshot: {diagnostics['screenshot_path']} "
                f"| URL: {diagnostics['url']} "
                f"| Title: {diagnostics['title']}"
            ) from exc

    @classmethod
    def assert_text_equals(
        cls,
        page: Page,
        actual_text: str,
        expected_text: str,
        failure_message: str,
        diagnostic_name: str,
    ) -> None:
        try:
            CommonAssertions.assert_equals(
                actual_text,
                expected_text,
                failure_message,
            )
            cls.LOGGER.info(
                "UI assertion passed: text equals expected value. Expected=%s | Actual=%s",
                expected_text,
                actual_text,
            )
        except AssertionError as exc:
            diagnostics = FailureDiagnosticsUtils.capture_page_diagnostics(page, diagnostic_name)
            raise AssertionError(
                f"{failure_message} | Expected text: {expected_text!r} | Actual text: {actual_text!r} "
                f"| Screenshot: {diagnostics['screenshot_path']} "
                f"| URL: {diagnostics['url']}"
            ) from exc

    @classmethod
    def assert_count_greater_than(
        cls,
        page: Page,
        actual_count: int,
        threshold: int,
        failure_message: str,
        diagnostic_name: str,
    ) -> None:
        try:
            CommonAssertions.assert_greater_than(
                actual_count,
                threshold,
                failure_message,
            )
            cls.LOGGER.info(
                "UI assertion passed: count greater than threshold. Threshold=%s | Actual=%s",
                threshold,
                actual_count,
            )
        except AssertionError as exc:
            diagnostics = FailureDiagnosticsUtils.capture_page_diagnostics(page, diagnostic_name)
            raise AssertionError(
                f"{failure_message} | Expected count greater than: {threshold!r} | Actual count: {actual_count!r} "
                f"| Screenshot: {diagnostics['screenshot_path']} "
                f"| URL: {diagnostics['url']}"
            ) from exc