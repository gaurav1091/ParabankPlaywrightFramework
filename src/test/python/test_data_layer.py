import pytest

from com.parabank.automation.models.login_data import LoginData
from com.parabank.automation.utils.data_provider import DataProvider


pytestmark = [pytest.mark.sanity]


def test_login_data_model_mapping() -> None:
    data = LoginData.from_dict({
        "username": "test_user",
        "password": "test_pass"
    })

    assert data.username == "test_user"
    assert data.password == "test_pass"


def test_json_reader_single_entry() -> None:
    login_data = DataProvider.get_login_data(
        "login/login_test_data.json",
        "invalidLogin"
    )

    assert login_data.username == "invalid_user"
    assert login_data.password == "invalid_pass"


def test_json_reader_all_entries() -> None:
    all_data = DataProvider.get_all_login_data(
        "login/login_test_data.json"
    )

    assert len(all_data) == 3

    usernames = [data.username for data in all_data]

    assert "invalid_user" in usernames
    assert "" in usernames
    assert "john" in usernames