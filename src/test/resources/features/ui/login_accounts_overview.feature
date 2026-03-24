@ui @smoke @regression
Feature: Login and Accounts Overview

  @ui @smoke
  Scenario: Valid user logs in and views accounts overview
    Given the user opens the Parabank login page
    When the user logs in with valid credentials
    Then the user should be successfully logged in
    And the accounts overview page should be displayed
    And the accounts table should contain at least one account