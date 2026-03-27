import pytest
from pytest_bdd import scenarios


pytestmark = [pytest.mark.ui, pytest.mark.regression]

scenarios("../../../resources/features/ui/find_transactions.feature")