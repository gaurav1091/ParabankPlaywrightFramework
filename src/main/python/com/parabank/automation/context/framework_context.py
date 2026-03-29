from playwright.sync_api import Page

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.context.scenario_context import ScenarioContext


class FrameworkContext:
    def __init__(self, page: Page, config_manager: ConfigManager) -> None:
        self.page = page
        self.config_manager = config_manager
        self.scenario_context = ScenarioContext()

        # Hybrid shared state
        self.customer_id: int | None = None
        self.cookie_header: str | None = None
        self.ui_account_ids: list[int] = []
        self.api_account_ids: list[int] = []

    def reset_hybrid_state(self) -> None:
        self.customer_id = None
        self.cookie_header = None
        self.ui_account_ids = []
        self.api_account_ids = []
