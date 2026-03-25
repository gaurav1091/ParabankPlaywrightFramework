import re


class CustomerUtils:
    @staticmethod
    def extract_customer_id_from_page_source(page_source: str) -> int:
        """
        Java-parity extraction:
        Look for a pattern like:
        customers/<customerId>/accounts
        anywhere in the page source.
        """
        match = re.search(r"customers/.*?(\d+).*?/accounts", page_source, re.DOTALL)

        if match:
            return int(match.group(1))

        raise ValueError("Unable to extract customerId from page source.")