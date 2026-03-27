from __future__ import annotations

from com.parabank.automation.dataproviders.base_test_data_provider import BaseTestDataProvider
from com.parabank.automation.models.find_transactions_test_data import FindTransactionsTestData


class FindTransactionsTestDataProvider(BaseTestDataProvider):
    FIND_TRANSACTIONS_TEST_DATA_FILE = "find_transactions/find_transactions_test_data.json"

    @classmethod
    def get_find_transactions_test_data_by_key(cls, key: str) -> FindTransactionsTestData:
        return cls.get_test_data_by_key(
            file_name=cls.FIND_TRANSACTIONS_TEST_DATA_FILE,
            key=key,
            mapper=FindTransactionsTestData.from_dict,
        )