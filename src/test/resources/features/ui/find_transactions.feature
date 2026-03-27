@ui @regression
Feature: Find Transactions

  @ui @regression
  Scenario: Valid user finds transactions by transferred amount
    Given the user opens the Parabank login page
    When the user logs in with valid credentials
    Then the user should be successfully logged in
    When the user completes a transfer using find transactions test data key "smallTransactionSearch"
    And the user navigates to the Find Transactions page
    Then the Find Transactions page should be displayed
    When the user searches transactions by amount using the same test data key "smallTransactionSearch"
    Then matching transactions should be displayed
    And the displayed transaction amount should match the searched amount