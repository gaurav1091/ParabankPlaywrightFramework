from __future__ import annotations

from com.parabank.automation.dataproviders.base_test_data_provider import BaseTestDataProvider
from com.parabank.automation.models.login_data import LoginData


class LoginTestDataProvider(BaseTestDataProvider):
    LOGIN_TEST_DATA_FILE = "login/login_test_data.json"

    @classmethod
    def get_login_test_data_by_key(cls, key: str) -> LoginData:
        return cls.get_test_data_by_key(
            file_name=cls.LOGIN_TEST_DATA_FILE,
            key=key,
            mapper=LoginData.from_dict,
        )