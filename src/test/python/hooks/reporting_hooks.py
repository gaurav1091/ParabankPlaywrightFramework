from __future__ import annotations

import shutil
from pathlib import Path

import allure
import pytest

from com.parabank.automation.utils.framework_logger import FrameworkLogger
from com.parabank.automation.utils.screenshot_utils import ScreenshotUtils


LOGGER = FrameworkLogger.get_logger("parabank_framework.reporting_hooks")

REPORTS_DIR = Path("test-output/reports")
REPORT_IMAGES_DIR = REPORTS_DIR / "images"


def _safe_failed_page(item: pytest.Item):
    page = item.funcargs.get("framework_page") if hasattr(item, "funcargs") else None

    if page is None:
        return None

    try:
        if page.is_closed():
            return None
    except Exception:
        return None

    return page


def _attach_screenshot_to_allure(screenshot_path: str) -> None:
    path = Path(screenshot_path)
    if path.exists():
        allure.attach.file(
            str(path),
            name="failure_screenshot",
            attachment_type=allure.attachment_type.PNG,
        )


def _attach_text_to_allure(name: str, value: str) -> None:
    allure.attach(
        value,
        name=name,
        attachment_type=allure.attachment_type.TEXT,
    )


def _copy_screenshot_into_report_assets(screenshot_path: str) -> str:
    source_path = Path(screenshot_path)
    REPORT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    destination_path = REPORT_IMAGES_DIR / source_path.name
    shutil.copy2(source_path, destination_path)

    # return path relative to report.html
    return f"images/{destination_path.name}"


def _build_report_image_html(relative_image_path: str) -> str:
    return f"""
    <div style="margin-top:10px;">
        <div style="font-weight:bold; margin-bottom:6px;">Failure Screenshot</div>
        <a href="{relative_image_path}" target="_blank">Open screenshot</a><br/><br/>
        <img src="{relative_image_path}"
             alt="failure_screenshot"
             style="max-width:900px; border:1px solid #ccc;" />
    </div>
    """


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()

    setattr(item, f"rep_{report.when}", report)

    if report.when not in {"setup", "call"}:
        return

    if not report.failed:
        return

    page = _safe_failed_page(item)
    if page is None:
        LOGGER.info("No active page available for failure screenshot. Node=%s", item.nodeid)
        return

    screenshot_name = f"failure_{item.nodeid}_{report.when}"
    screenshot_path = ScreenshotUtils.capture_page_screenshot(
        page,
        screenshot_name,
        full_page=True,
    )

    LOGGER.info(
        "Failure screenshot captured. Node=%s | Phase=%s | Screenshot=%s",
        item.nodeid,
        report.when,
        screenshot_path,
    )

    pytest_html = item.config.pluginmanager.getplugin("html")
    if pytest_html is not None:
        extras = getattr(report, "extras", [])

        try:
            relative_image_path = _copy_screenshot_into_report_assets(screenshot_path)
            image_html = _build_report_image_html(relative_image_path)
            extras.append(pytest_html.extras.html(image_html))
        except Exception as exc:
            LOGGER.warning(
                "Failed embedding screenshot into pytest-html report. Node=%s | Error=%s",
                item.nodeid,
                exc,
            )
            extras.append(pytest_html.extras.text(f"Screenshot path: {screenshot_path}"))

        extras.append(pytest_html.extras.text(f"Failure phase: {report.when}"))
        extras.append(pytest_html.extras.text(f"Current URL: {page.url}"))
        extras.append(pytest_html.extras.text(f"Page title: {page.title()}"))
        report.extras = extras

    try:
        _attach_screenshot_to_allure(screenshot_path)
        _attach_text_to_allure("failure_phase", report.when)
        _attach_text_to_allure("failure_url", page.url)
        _attach_text_to_allure("failure_title", page.title())
    except Exception as exc:
        LOGGER.warning(
            "Failed attaching screenshot metadata to Allure. Node=%s | Error=%s",
            item.nodeid,
            exc,
        )