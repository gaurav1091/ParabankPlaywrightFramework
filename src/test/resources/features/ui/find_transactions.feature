@ui @regression
Feature: Find Transactions

  @ui @findtransactions @regression @positive
  Scenario Outline: Valid user finds transactions by amount after performing a transfer
    Given the user opens the Parabank login page
    When the user logs in with valid credentials
    Then the user should be successfully logged in
    When the user completes a transfer using find transactions test data key "<testDataKey>"
    And the user navigates to the Find Transactions page
    Then the Find Transactions page should be displayed
    When the user searches transactions by amount using the same test data key "<testDataKey>"
    Then matching transactions should be displayed
    And the displayed transaction amount should match the searched amount
    And the search results should be correct for the searched account and amount

    Examples:
      | testDataKey               |
      | transferTransactionSmall  |
      | transferTransactionMedium |