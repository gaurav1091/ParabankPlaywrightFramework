import json
import os
import urllib.parse


class BrowserStackConfig:
    @staticmethod
    def _build_worker_aware_session_name(base_name: str) -> str:
        worker_id = os.getenv("PYTEST_XDIST_WORKER", "").strip()

        if not worker_id or worker_id == "master":
            return base_name

        return f"{base_name} [{worker_id}]"

    @staticmethod
    def build_caps(config_manager) -> dict:
        session_name = BrowserStackConfig._build_worker_aware_session_name(
            config_manager.get_browserstack_session_name()
        )

        return {
            "browser": config_manager.get_browser(),
            "browser_version": config_manager.get_browserstack_browser_version(),
            "os": config_manager.get_browserstack_os(),
            "os_version": config_manager.get_browserstack_os_version(),
            "project": config_manager.get_browserstack_project_name(),
            "build": config_manager.get_browserstack_build_name(),
            "name": session_name,
            "browserstack.debug": config_manager.is_browserstack_debug_enabled(),
            "browserstack.networkLogs": config_manager.is_browserstack_network_logs_enabled(),
            "browserstack.console": config_manager.get_browserstack_console_logs(),
        }

    @staticmethod
    def get_ws_endpoint(config_manager) -> str:
        username = config_manager.get_browserstack_username()
        access_key = config_manager.get_browserstack_access_key()

        if not username or not access_key:
            raise ValueError(
                "BrowserStack credentials are missing. "
                "Set browserstack.username and browserstack.access.key in the active properties file."
            )

        caps = BrowserStackConfig.build_caps(config_manager)
        caps["browserstack.username"] = username
        caps["browserstack.accessKey"] = access_key

        encoded_caps = urllib.parse.quote(json.dumps(caps))
        return f"wss://cdp.browserstack.com/playwright?caps={encoded_caps}"