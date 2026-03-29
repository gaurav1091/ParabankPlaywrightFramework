Feature: Hybrid account creation validation

  @hybrid @apiui @regression @serial
  Scenario Outline: Create a new account in UI and validate it through API
    Given user logs in for hybrid account creation using key "<key>"
    When user captures current account details from UI and API before account creation
    And user creates a new account in UI using hybrid account creation key "<key>"
    And user refreshes account details from UI and API after account creation
    Then the new account should be present in both UI and API account lists
    And account count should increase by one in both UI and API

    Examples:
      | key                          |
      | hybridSavingsAccountCreation |
      | hybridCheckingAccountCreation |