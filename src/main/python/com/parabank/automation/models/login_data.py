from dataclasses import dataclass


@dataclass
class LoginData:
    username: str
    password: str

    @staticmethod
    def from_dict(data: dict) -> "LoginData":
        return LoginData(
            username=data.get("username", ""),
            password=data.get("password", ""),
        )