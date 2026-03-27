@ui @regression
Feature: Bill Pay

  @ui @regression
  Scenario: Valid user submits a bill payment
    Given the user opens the Parabank login page
    When the user logs in with valid credentials
    Then the user should be successfully logged in
    When the user navigates to the Bill Pay page
    Then the Bill Pay page should be displayed
    When the user submits the bill payment using test data key "electricityPayment"
    Then the bill payment should be completed successfully