Feature: Customer API validation

  @api @api_authenticated @regression
  Scenario: Validate authenticated customer account ids from API match UI
    Given authenticated API session is prepared using browser-backed login
    When user requests account details through API for the authenticated customer
    Then accounts API response status should be 200
    And API account ids should match the UI account ids from the authenticated session