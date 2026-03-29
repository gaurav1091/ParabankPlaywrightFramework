import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.hybrid,
    pytest.mark.apiui,
    pytest.mark.regression,
    pytest.mark.serial,
    pytest.mark.ui,
    pytest.mark.api,
]

scenarios("../../../resources/features/hybrid/account_creation_hybrid.feature")
