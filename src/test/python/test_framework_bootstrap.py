from com.parabank.automation.config.config_manager import ConfigManager


def test_framework_config_bootstraps(framework_config: ConfigManager) -> None:
    assert framework_config is not None
    assert framework_config.get_current_environment() == "qa"
    assert framework_config.get_browser() == "chrome"
    assert framework_config.is_headless() is False
    assert framework_config.get_base_url() == "https://parabank.parasoft.com/parabank"
    assert framework_config.get_api_base_url() == "https://parabank.parasoft.com/parabank/services_proxy/bank"
    assert framework_config.get_thread_count() == 3
    assert framework_config.get_data_provider_thread_count() == 3
    assert framework_config.is_retry_enabled() is True
    assert framework_config.get_retry_count() == 1