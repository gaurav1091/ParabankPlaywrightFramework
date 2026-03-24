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
            raise AssertionError(
                f"{message} | Expected: {expected!r} | Actual: {actual!r}"
            )

    @staticmethod
    def assert_not_equals(actual, unexpected, message: str) -> None:
        if actual == unexpected:
            raise AssertionError(
                f"{message} | Unexpected value encountered: {unexpected!r}"
            )

    @staticmethod
    def assert_contains(container, member, message: str) -> None:
        if member not in container:
            raise AssertionError(
                f"{message} | Expected member: {member!r} not found in: {container!r}"
            )

    @staticmethod
    def assert_not_none(value, message: str) -> None:
        if value is None:
            raise AssertionError(message)

    @staticmethod
    def assert_greater_than(actual, threshold, message: str) -> None:
        if actual <= threshold:
            raise AssertionError(
                f"{message} | Expected greater than: {threshold!r} | Actual: {actual!r}"
            )