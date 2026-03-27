@ui @regression
Feature: Login

  @ui @login @smoke @regression @positive
  Scenario Outline: Successful login with valid centralized JSON test data
    Given the user opens the Parabank login page
    When the user logs in with valid test data key "<testDataKey>"
    Then the user should be navigated to the home page
    And the logout link should be visible

    Examples:
      | testDataKey |
      | validUser   |

  @ui @login @negative @quarantined
  Scenario Outline: Login with invalid centralized JSON test data
    Given the user opens the Parabank login page
    When the user attempts login failure with test data key "<testDataKey>"
    Then the user should see the login error message

    Examples:
      | testDataKey            |
      | invalidUser            |
      | validUserWrongPassword |
      | wrongUserValidPassword |