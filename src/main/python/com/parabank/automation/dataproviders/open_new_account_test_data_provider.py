from __future__ import annotations

from com.parabank.automation.dataproviders.base_test_data_provider import BaseTestDataProvider
from com.parabank.automation.models.open_new_account_test_data import OpenNewAccountTestData


class OpenNewAccountTestDataProvider(BaseTestDataProvider):
    OPEN_NEW_ACCOUNT_TEST_DATA_FILE = "open_new_account/open_new_account_test_data.json"

    @classmethod
    def get_open_new_account_test_data_by_key(cls, key: str) -> OpenNewAccountTestData:
        return cls.get_test_data_by_key(
            file_name=cls.OPEN_NEW_ACCOUNT_TEST_DATA_FILE,
            key=key,
            mapper=OpenNewAccountTestData.from_dict,
        )
