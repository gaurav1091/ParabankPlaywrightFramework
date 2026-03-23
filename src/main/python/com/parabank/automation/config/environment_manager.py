from com.parabank.automation.config.framework_constants import FrameworkConstants
from com.parabank.automation.enums.environment_type import EnvironmentType


class EnvironmentManager:
    @staticmethod
    def get_current_environment(explicit_env: str | None = None) -> str:
        current_environment = (explicit_env or "qa").strip().lower()

        if current_environment not in FrameworkConstants.SUPPORTED_ENVIRONMENTS:
            raise ValueError(
                f"Unsupported environment: {current_environment}. "
                f"Supported values: qa, stage, dev."
            )

        return current_environment

    @staticmethod
    def get_environment_type(explicit_env: str | None = None) -> EnvironmentType:
        environment = EnvironmentManager.get_current_environment(explicit_env)

        if environment == EnvironmentType.QA.value:
            return EnvironmentType.QA
        if environment == EnvironmentType.STAGE.value:
            return EnvironmentType.STAGE
        if environment == EnvironmentType.DEV.value:
            return EnvironmentType.DEV

        raise ValueError(f"Unsupported environment: {environment}")

    @staticmethod
    def get_environment_config_file_name(explicit_env: str | None = None) -> str:
        environment_type = EnvironmentManager.get_environment_type(explicit_env)

        if environment_type == EnvironmentType.QA:
            return FrameworkConstants.QA_CONFIG_FILE
        if environment_type == EnvironmentType.STAGE:
            return FrameworkConstants.STAGE_CONFIG_FILE
        if environment_type == EnvironmentType.DEV:
            return FrameworkConstants.DEV_CONFIG_FILE

        raise ValueError(f"Unsupported environment: {environment_type.value}")