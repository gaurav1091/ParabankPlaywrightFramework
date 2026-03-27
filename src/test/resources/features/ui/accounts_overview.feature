@ui @regression
Feature: Accounts Overview

  @ui @regression
  Scenario: Valid user views the accounts overview page
    Given the user opens the Parabank login page
    When the user logs in with valid credentials
    Then the user should be successfully logged in
    When the user navigates to the Accounts Overview page
    Then the accounts overview page should be displayed
    And the accounts table should contain at least one account