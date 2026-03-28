@ui @regression
Feature: Bill Pay

  @ui @billpay @regression @positive
  Scenario Outline: Valid user submits a bill payment with centralized JSON test data
    Given the user opens the Parabank login page
    When the user logs in with valid credentials
    Then the user should be successfully logged in
    When the user navigates to the Bill Pay page
    Then the Bill Pay page should be displayed
    When the user submits the bill payment using test data key "<testDataKey>"
    Then the bill payment should be completed successfully

    Examples:
      | testDataKey        |
      | electricityPayment |
      | waterBillPayment   |