import pytest
from pytest_bdd import scenarios

pytestmark = [
    pytest.mark.hybrid,
    pytest.mark.apiui,
    pytest.mark.smoke,
    pytest.mark.regression,
    pytest.mark.ui,
    pytest.mark.api,
]

scenarios("../../../resources/features/hybrid/account_hybrid.feature")
