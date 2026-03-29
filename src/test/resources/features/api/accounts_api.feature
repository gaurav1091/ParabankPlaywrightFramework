Feature: Accounts API validation

  @api @api_authenticated @smoke @regression
  Scenario: Validate authenticated customer accounts API response structure
    Given authenticated API session is prepared using browser-backed login
    When user requests account details through API for the authenticated customer
    Then accounts API response status should be 200
    And accounts API response should contain at least one account
    And each account should contain valid core details