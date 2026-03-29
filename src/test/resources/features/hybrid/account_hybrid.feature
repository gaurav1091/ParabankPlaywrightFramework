Feature: Hybrid account validation

  @hybrid @apiui @smoke @regression
  Scenario Outline: Validate account numbers through UI and API using centralized hybrid data
    Given user performs hybrid login with test data key "<key>"
    When user opens accounts overview and captures account details from UI
    And user fetches account details from API for the same customer
    Then API and UI account numbers should match

    Examples:
      | key                     |
      | hybridAccountValidation |