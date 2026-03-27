from __future__ import annotations

from com.parabank.automation.base.base_page import BasePage


class BillPayPage(BasePage):
    PAGE_HEADING = "css=div#billpayForm h1.title"

    PAYEE_NAME_INPUT = "input[name='payee.name']"
    ADDRESS_INPUT = "input[name='payee.address.street']"
    CITY_INPUT = "input[name='payee.address.city']"
    STATE_INPUT = "input[name='payee.address.state']"
    ZIP_CODE_INPUT = "input[name='payee.address.zipCode']"
    PHONE_NUMBER_INPUT = "input[name='payee.phoneNumber']"
    ACCOUNT_NUMBER_INPUT = "input[name='payee.accountNumber']"
    VERIFY_ACCOUNT_INPUT = "input[name='verifyAccount']"
    AMOUNT_INPUT = "input[name='amount']"
    FROM_ACCOUNT_DROPDOWN = "select[name='fromAccountId']"
    SEND_PAYMENT_BUTTON = "input[value='Send Payment']"

    PAYMENT_COMPLETE_HEADING = "css=div#billpayResult h1.title"
    PAYMENT_RESULT_MESSAGE = "css=div#billpayResult p"

    def is_page_heading_visible(self) -> bool:
        return self.is_visible(self.PAGE_HEADING)

    def get_page_heading_text(self) -> str:
        return self.get_text(self.PAGE_HEADING)

    def is_bill_pay_page_loaded(self) -> bool:
        return (
            self.is_page_heading_visible()
            and self.is_visible(self.PAYEE_NAME_INPUT)
            and self.is_visible(self.AMOUNT_INPUT)
            and self.is_visible(self.FROM_ACCOUNT_DROPDOWN)
            and self.is_visible(self.SEND_PAYMENT_BUTTON)
        )

    def enter_payee_name(self, payee_name: str) -> "BillPayPage":
        self.logger.info("Entering payee name: %s", payee_name)
        self._fill_and_verify(self.PAYEE_NAME_INPUT, payee_name)
        return self

    def enter_address(self, address: str) -> "BillPayPage":
        self.logger.info("Entering address.")
        self._fill_and_verify(self.ADDRESS_INPUT, address)
        return self

    def enter_city(self, city: str) -> "BillPayPage":
        self.logger.info("Entering city: %s", city)
        self._fill_and_verify(self.CITY_INPUT, city)
        return self

    def enter_state(self, state: str) -> "BillPayPage":
        self.logger.info("Entering state: %s", state)
        self._fill_and_verify(self.STATE_INPUT, state)
        return self

    def enter_zip_code(self, zip_code: str) -> "BillPayPage":
        self.logger.info("Entering zip code: %s", zip_code)
        self._fill_and_verify(self.ZIP_CODE_INPUT, zip_code)
        return self

    def enter_phone_number(self, phone_number: str) -> "BillPayPage":
        self.logger.info("Entering phone number: %s", phone_number)
        self._fill_and_verify(self.PHONE_NUMBER_INPUT, phone_number)
        return self

    def enter_account_number(self, account_number: str) -> "BillPayPage":
        self.logger.info("Entering account number: %s", account_number)
        self._fill_and_verify(self.ACCOUNT_NUMBER_INPUT, account_number)
        return self

    def enter_verify_account_number(self, account_number: str) -> "BillPayPage":
        self.logger.info("Entering verify account number.")
        self._fill_and_verify(self.VERIFY_ACCOUNT_INPUT, account_number)
        return self

    def enter_amount(self, amount: str) -> "BillPayPage":
        self.logger.info("Entering bill payment amount: %s", amount)
        self._fill_and_verify(self.AMOUNT_INPUT, amount)
        return self

    def select_first_valid_from_account(self) -> "BillPayPage":
        self.logger.info("Selecting first valid source account for bill pay.")
        self.select_first_valid_dropdown_option(self.FROM_ACCOUNT_DROPDOWN, ignore_texts={"Select Account"})
        return self

    def get_first_valid_from_account(self) -> str:
        options = self.get_dropdown_options_text(self.FROM_ACCOUNT_DROPDOWN)
        for option in options:
            if option.strip() and option.strip().lower() != "select account":
                return option
        raise RuntimeError("No valid source account option was found in Bill Pay dropdown.")

    def get_selected_from_account(self) -> str:
        selected_text = self.get_selected_dropdown_text(self.FROM_ACCOUNT_DROPDOWN)
        self.logger.info("Selected bill-pay source account: %s", selected_text)
        return selected_text

    def click_send_payment_button(self) -> "BillPayPage":
        self.logger.info("Clicking Send Payment button.")
        self.click(self.SEND_PAYMENT_BUTTON)
        self.wait_for_page_ready()
        return self

    def submit_bill_payment(
        self,
        payee_name: str,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        phone_number: str,
        account_number: str,
        amount: str,
    ) -> "BillPayPage":
        self.logger.info("Submitting bill payment for payee: %s", payee_name)
        return (
            self.enter_payee_name(payee_name)
            .enter_address(address)
            .enter_city(city)
            .enter_state(state)
            .enter_zip_code(zip_code)
            .enter_phone_number(phone_number)
            .enter_account_number(account_number)
            .enter_verify_account_number(account_number)
            .enter_amount(amount)
            .select_first_valid_from_account()
            .click_send_payment_button()
        )

    def is_bill_payment_successful(self) -> bool:
        return self.is_visible(self.PAYMENT_COMPLETE_HEADING) and self.is_visible(self.PAYMENT_RESULT_MESSAGE)

    def get_bill_payment_complete_heading_text(self) -> str:
        return self.get_text(self.PAYMENT_COMPLETE_HEADING).strip()

    def get_bill_payment_result_message(self) -> str:
        return self.get_text(self.PAYMENT_RESULT_MESSAGE).strip()

    def _fill_and_verify(self, selector: str, value: str) -> None:
        self.clear_and_enter_text(selector, value)
        actual_value = self.get_input_value(selector)

        if actual_value != value:
            self.logger.warning(
                "Field value mismatch after fill. Selector=%s | Expected=%s | Actual=%s. Retrying with JS.",
                selector,
                value,
                actual_value,
            )
            locator = self.get_locator(selector)
            self.page.evaluate("(element, val) => element.value = val", locator.element_handle(), value)