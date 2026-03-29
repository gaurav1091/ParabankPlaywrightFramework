from __future__ import annotations

from pytest_bdd import then

from com.parabank.automation.assertions.api_assertions import ApiAssertions


@then("API account ids should match the UI account ids from the authenticated session")
def api_account_ids_should_match_the_ui_account_ids_from_the_authenticated_session(
    authenticated_api_context: dict,
    authenticated_accounts_api_result: dict,
) -> None:
    ui_account_ids = authenticated_api_context["ui_account_ids"]
    api_account_ids = authenticated_accounts_api_result["account_ids_from_payload"]

    ApiAssertions.assert_list_not_empty(
        ui_account_ids,
        "UI account ids were not captured during authenticated API setup.",
    )
    ApiAssertions.assert_list_not_empty(
        api_account_ids,
        "API account ids were not captured.",
    )
    ApiAssertions.assert_collections_match_ignoring_order(
        api_account_ids,
        ui_account_ids,
        "API account ids do not match UI account ids.",
    )