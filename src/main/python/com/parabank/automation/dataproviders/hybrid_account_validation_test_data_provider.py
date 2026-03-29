from __future__ import annotations

from com.parabank.automation.dataproviders.base_test_data_provider import BaseTestDataProvider
from com.parabank.automation.models.hybrid_account_validation_test_data import HybridAccountValidationTestData


class HybridAccountValidationTestDataProvider(BaseTestDataProvider):
    HYBRID_ACCOUNT_VALIDATION_TEST_DATA_FILE = "hybrid/hybrid_account_validation_test_data.json"

    @classmethod
    def get_hybrid_account_validation_test_data_by_key(cls, key: str) -> HybridAccountValidationTestData:
        return cls.get_test_data_by_key(
            file_name=cls.HYBRID_ACCOUNT_VALIDATION_TEST_DATA_FILE,
            key=key,
            mapper=HybridAccountValidationTestData.from_dict,
        )