@ui @regression
Feature: Login

  @ui @regression
  Scenario: Valid user logs in successfully
    Given the user opens the Parabank login page
    When the user logs in with valid credentials
    Then the user should be successfully logged in