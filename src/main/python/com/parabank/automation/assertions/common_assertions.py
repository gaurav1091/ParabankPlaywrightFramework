from __future__ import annotations


class CommonAssertions:
    @staticmethod
    def assert_true(actual: bool, message: str) -> None:
        if actual is not True:
            raise AssertionError(message)

    @staticmethod
    def assert_false(actual: bool, message: str) -> None:
        if actual is not False:
            raise AssertionError(message)

    @staticmethod
    def assert_equals(actual, expected, message: str) -> None:
        if actual != expected:
            raise AssertionError(f"{message} | Expected: {expected!r} | Actual: {actual!r}")

    @staticmethod
    def assert_not_equals(actual, unexpected, message: str) -> None:
        if actual == unexpected:
            raise AssertionError(f"{message} | Unexpected value encountered: {unexpected!r}")

    @staticmethod
    def assert_contains(container, member, message: str) -> None:
        if member not in container:
            raise AssertionError(f"{message} | Expected member: {member!r} not found in: {container!r}")

    @staticmethod
    def assert_not_contains(container, member, message: str) -> None:
        if member in container:
            raise AssertionError(f"{message} | Unexpected member: {member!r} found in: {container!r}")

    @staticmethod
    def assert_not_none(value, message: str) -> None:
        if value is None:
            raise AssertionError(message)

    @staticmethod
    def assert_none(value, message: str) -> None:
        if value is not None:
            raise AssertionError(f"{message} | Expected None but found: {value!r}")

    @staticmethod
    def assert_greater_than(actual, threshold, message: str) -> None:
        if actual <= threshold:
            raise AssertionError(f"{message} | Expected greater than: {threshold!r} | Actual: {actual!r}")

    @staticmethod
    def assert_not_empty(value, message: str) -> None:
        if value is None:
            raise AssertionError(f"{message} | Value is None.")

        if hasattr(value, "__len__") and len(value) == 0:
            raise AssertionError(f"{message} | Value is empty: {value!r}")

        if isinstance(value, str) and not value.strip():
            raise AssertionError(f"{message} | String value is blank.")

    @staticmethod
    def assert_is_instance(value, expected_type, message: str) -> None:
        if not isinstance(value, expected_type):
            raise AssertionError(f"{message} | Expected type: {expected_type!r} | Actual type: {type(value)!r}")

    @staticmethod
    def assert_list_not_empty(values: list, message: str) -> None:
        if values is None or not isinstance(values, list) or len(values) == 0:
            raise AssertionError(message)
