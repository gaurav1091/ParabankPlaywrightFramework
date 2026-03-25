from dataclasses import dataclass


@dataclass
class EnvironmentReadiness:
    selected_data_access_mode: str
    rest_endpoint_value: str
    rest_hybrid_supported: bool
    reason: str