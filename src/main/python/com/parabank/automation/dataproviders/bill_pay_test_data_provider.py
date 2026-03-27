from __future__ import annotations

from com.parabank.automation.dataproviders.base_test_data_provider import BaseTestDataProvider
from com.parabank.automation.models.bill_pay_test_data import BillPayTestData


class BillPayTestDataProvider(BaseTestDataProvider):
    BILL_PAY_TEST_DATA_FILE = "bill_pay/bill_pay_test_data.json"

    @classmethod
    def get_bill_pay_test_data_by_key(cls, key: str) -> BillPayTestData:
        return cls.get_test_data_by_key(
            file_name=cls.BILL_PAY_TEST_DATA_FILE,
            key=key,
            mapper=BillPayTestData.from_dict,
        )