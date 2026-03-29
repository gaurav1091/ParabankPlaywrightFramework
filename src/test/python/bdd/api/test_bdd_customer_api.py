import pytest
from pytest_bdd import scenarios

pytestmark = [pytest.mark.api, pytest.mark.regression]

scenarios("../../../resources/features/api/customer_api.feature")
