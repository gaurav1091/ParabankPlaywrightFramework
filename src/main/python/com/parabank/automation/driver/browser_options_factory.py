from com.parabank.automation.config.config_manager import ConfigManager


class BrowserOptionsFactory:
    @staticmethod
    def build_launch_options(config_manager: ConfigManager) -> dict:
        options: dict = {
            "headless": config_manager.is_headless(),
            "slow_mo": config_manager.get_playwright_slow_mo_millis(),
            "timeout": config_manager.get_playwright_browser_launch_timeout_millis(),
        }

        channel = config_manager.get_playwright_browser_channel()
        if channel:
            options["channel"] = channel

        return options

    @staticmethod
    def build_context_options(config_manager: ConfigManager) -> dict:
        options: dict = {
            "viewport": {
                "width": config_manager.get_playwright_viewport_width(),
                "height": config_manager.get_playwright_viewport_height(),
            },
            "accept_downloads": config_manager.is_playwright_accept_downloads_enabled(),
            "ignore_https_errors": config_manager.is_playwright_ignore_https_errors_enabled(),
        }

        if config_manager.is_playwright_video_enabled():
            options["record_video_dir"] = "test-output/videos"
            options["record_video_size"] = {
                "width": config_manager.get_playwright_video_width(),
                "height": config_manager.get_playwright_video_height(),
            }

        return options
