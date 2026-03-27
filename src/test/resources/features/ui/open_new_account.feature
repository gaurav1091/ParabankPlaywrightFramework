@ui @regression
Feature: Open New Account

  @ui @regression
  Scenario: Valid user creates a new savings account
    Given the user opens the Parabank login page
    When the user logs in with valid credentials
    Then the user should be successfully logged in
    When the user navigates to the Open New Account page
    Then the Open New Account page should be displayed
    When the user creates a new account using test data key "savingsAccount"
    Then the new account should be created successfully
    And the new account number should be displayed