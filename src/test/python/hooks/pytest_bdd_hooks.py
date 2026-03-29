import pytest
from pytest_bdd import given, scenarios, then, when


def pytest_bdd_apply_tag(tag, function):
    """
    Maps Gherkin tags to pytest markers.
    Example:
    @smoke -> pytest.mark.smoke
    """
    marker = getattr(pytest.mark, tag, None)
    if marker:
        marker(function)
    return function
