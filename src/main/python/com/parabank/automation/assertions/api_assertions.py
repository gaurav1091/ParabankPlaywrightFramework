from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator

from com.parabank.automation.assertions.common_assertions import CommonAssertions
from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.utils.framework_logger import FrameworkLogger


class ApiAssertions:
    LOGGER = FrameworkLogger.get_logger("parabank_framework.api_assertions")

    @classmethod
    def assert_status_code(cls, actual_status_code: int, expected_status_code: int, message: str) -> None:
        CommonAssertions.assert_equals(
            actual_status_code,
            expected_status_code,
            message,
        )
        cls.LOGGER.info(
            "API assertion passed: status code matched. Expected=%s | Actual=%s",
            expected_status_code,
            actual_status_code,
        )

    @classmethod
    def assert_response_is_dict(cls, payload: Any, message: str) -> None:
        CommonAssertions.assert_is_instance(payload, dict, message)
        cls.LOGGER.info("API assertion passed: payload is a dict.")

    @classmethod
    def assert_response_is_list(cls, payload: Any, message: str) -> None:
        CommonAssertions.assert_is_instance(payload, list, message)
        cls.LOGGER.info("API assertion passed: payload is a list.")

    @classmethod
    def assert_list_not_empty(cls, values: list, message: str) -> None:
        CommonAssertions.assert_list_not_empty(values, message)
        cls.LOGGER.info("API assertion passed: list is not empty. Count=%s", len(values))

    @classmethod
    def assert_collections_match_ignoring_order(
        cls,
        actual: list,
        expected: list,
        message: str,
    ) -> None:
        actual_sorted = sorted(actual)
        expected_sorted = sorted(expected)

        CommonAssertions.assert_equals(
            actual_sorted,
            expected_sorted,
            message,
        )
        cls.LOGGER.info(
            "API assertion passed: collections match ignoring order. Expected=%s | Actual=%s",
            expected_sorted,
            actual_sorted,
        )

    @classmethod
    def assert_collections_do_not_match_ignoring_order(
        cls,
        actual: list,
        unexpected: list,
        message: str,
    ) -> None:
        actual_sorted = sorted(actual)
        unexpected_sorted = sorted(unexpected)

        CommonAssertions.assert_not_equals(
            actual_sorted,
            unexpected_sorted,
            message,
        )
        cls.LOGGER.info(
            "API assertion passed: collections do not match ignoring order. Actual=%s | Unexpected=%s",
            actual_sorted,
            unexpected_sorted,
        )

    @classmethod
    def assert_field_present(cls, payload: dict, field_name: str, message: str) -> None:
        CommonAssertions.assert_is_instance(payload, dict, message)
        CommonAssertions.assert_true(
            field_name in payload,
            f"{message} | Missing field: {field_name!r}",
        )
        cls.LOGGER.info("API assertion passed: field is present. Field=%s", field_name)

    @classmethod
    def assert_not_empty_field(cls, payload: dict, field_name: str, message: str) -> None:
        CommonAssertions.assert_is_instance(payload, dict, message)
        CommonAssertions.assert_true(
            field_name in payload,
            f"{message} | Missing field: {field_name!r}",
        )
        CommonAssertions.assert_not_empty(
            payload.get(field_name),
            f"{message} | Field is empty: {field_name!r}",
        )
        cls.LOGGER.info("API assertion passed: field is present and not empty. Field=%s", field_name)

    @classmethod
    def assert_all_accounts_have_valid_core_fields(
        cls,
        accounts: list[dict[str, Any]],
        message: str,
    ) -> None:
        cls.assert_list_not_empty(accounts, f"{message} | Account list is empty.")

        for account in accounts:
            CommonAssertions.assert_is_instance(
                account,
                dict,
                f"{message} | Encountered non-dict account payload.",
            )

            account_id = account.get("id")
            balance = account.get("balance")

            CommonAssertions.assert_not_empty(
                account_id,
                f"{message} | Invalid or blank account id found.",
            )
            CommonAssertions.assert_not_none(
                balance,
                f"{message} | Account balance is null for account id: {account_id!r}",
            )

        cls.LOGGER.info(
            "API assertion passed: all accounts have valid core fields. Count=%s",
            len(accounts),
        )

    @classmethod
    def assert_json_matches_schema(
        cls,
        payload: Any,
        schema_relative_path: str,
        message: str,
    ) -> None:
        schema_path = Path(FrameworkConstants.SCHEMA_RESOURCES_ROOT) / schema_relative_path
        if not schema_path.exists():
            raise AssertionError(
                f"{message} | Schema file not found: {schema_path}"
            )

        with open(schema_path, "r", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)

        validator = Draft7Validator(schema)
        errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))

        if errors:
            formatted_errors = [
                f"path={list(error.path)} | message={error.message}"
                for error in errors
            ]
            raise AssertionError(
                f"{message} | Schema resource={schema_relative_path} | Violations={formatted_errors}"
            )

        cls.LOGGER.info(
            "API assertion passed: JSON matches schema. Schema=%s",
            schema_relative_path,
        )