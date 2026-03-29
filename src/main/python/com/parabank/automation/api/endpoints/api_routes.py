from __future__ import annotations


class ApiRoutes:
    CUSTOMER_ACCOUNTS_ROUTE = "customers/{customer_id}/accounts"

    @staticmethod
    def customer_accounts(customer_id: int | str) -> str:
        return ApiRoutes.CUSTOMER_ACCOUNTS_ROUTE.format(customer_id=customer_id)
