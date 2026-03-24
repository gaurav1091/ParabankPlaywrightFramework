from playwright.sync_api import Page

from com.parabank.automation.config.config_manager import ConfigManager
from com.parabank.automation.context.scenario_context import ScenarioContext


class FrameworkContext:
    def __init__(self, page: Page, config_manager: ConfigManager) -> None:
        self.page = page
        self.config_manager = config_manager
        self.scenario_context = ScenarioContext()