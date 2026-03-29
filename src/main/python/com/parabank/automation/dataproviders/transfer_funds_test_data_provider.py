from __future__ import annotations

from com.parabank.automation.dataproviders.base_test_data_provider import BaseTestDataProvider
from com.parabank.automation.models.transfer_funds_test_data import TransferFundsTestData


class TransferFundsTestDataProvider(BaseTestDataProvider):
    TRANSFER_FUNDS_TEST_DATA_FILE = "transfer_funds/transfer_funds_test_data.json"

    @classmethod
    def get_transfer_funds_test_data_by_key(cls, key: str) -> TransferFundsTestData:
        return cls.get_test_data_by_key(
            file_name=cls.TRANSFER_FUNDS_TEST_DATA_FILE,
            key=key,
            mapper=TransferFundsTestData.from_dict,
        )
