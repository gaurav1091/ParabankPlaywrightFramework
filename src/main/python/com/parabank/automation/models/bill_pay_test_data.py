from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BillPayTestData:
    key: str
    payee_name: str
    address: str
    city: str
    state: str
    zip_code: str
    phone_number: str
    account_number: str
    amount: str

    @classmethod
    def from_dict(cls, data: dict) -> "BillPayTestData":
        return cls(
            key=str(data.get("key", "")).strip(),
            payee_name=str(data.get("payeeName", "")).strip(),
            address=str(data.get("address", "")).strip(),
            city=str(data.get("city", "")).strip(),
            state=str(data.get("state", "")).strip(),
            zip_code=str(data.get("zipCode", "")).strip(),
            phone_number=str(data.get("phoneNumber", "")).strip(),
            account_number=str(data.get("accountNumber", "")).strip(),
            amount=str(data.get("amount", "")).strip(),
        )