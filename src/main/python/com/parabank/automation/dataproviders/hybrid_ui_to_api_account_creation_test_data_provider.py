from __future__ import annotations

from com.parabank.automation.dataproviders.base_test_data_provider import BaseTestDataProvider
from com.parabank.automation.models.hybrid_ui_to_api_account_creation_test_data import (
    HybridUiToApiAccountCreationTestData,
)


class HybridUiToApiAccountCreationTestDataProvider(BaseTestDataProvider):
    HYBRID_UI_TO_API_ACCOUNT_CREATION_TEST_DATA_FILE = "hybrid/hybrid_ui_to_api_account_creation_test_data.json"

    @classmethod
    def get_by_key(cls, key: str) -> HybridUiToApiAccountCreationTestData:
        return cls.get_test_data_by_key(
            file_name=cls.HYBRID_UI_TO_API_ACCOUNT_CREATION_TEST_DATA_FILE,
            key=key,
            mapper=HybridUiToApiAccountCreationTestData.from_dict,
        )