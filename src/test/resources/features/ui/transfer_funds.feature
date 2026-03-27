@ui @regression
Feature: Transfer Funds

  @ui @regression
  Scenario: Valid user transfers funds
    Given the user opens the Parabank login page
    When the user logs in with valid credentials
    Then the user should be successfully logged in
    When the user navigates to the Transfer Funds page
    Then the Transfer Funds page should be displayed
    When the user transfers funds using test data key "smallTransfer"
    Then the transfer should be completed successfully
    And the transferred amount should be displayed correctly