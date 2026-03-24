from typing import List

from com.parabank.automation.models.login_data import LoginData
from com.parabank.automation.utils.json_reader import JsonReader


class DataProvider:

    @staticmethod
    def get_login_data(relative_path: str, key: str) -> LoginData:
        data = JsonReader.read_json_by_key(relative_path, key)
        return LoginData.from_dict(data)

    @staticmethod
    def get_all_login_data(relative_path: str) -> List[LoginData]:
        raw_data = JsonReader.read_json(relative_path)

        return [
            LoginData.from_dict(value)
            for value in raw_data.values()
        ]