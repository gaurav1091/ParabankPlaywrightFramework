import pytest
from pytest_bdd import scenarios


pytestmark = [pytest.mark.ui, pytest.mark.smoke, pytest.mark.regression]

scenarios("../../../resources/features/ui/login_accounts_overview.feature")