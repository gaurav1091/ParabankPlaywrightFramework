from pathlib import Path

from com.parabank.automation.exceptions.config_file_exception import ConfigFileException


class PropertyReader:
    @staticmethod
    def load_properties(file_path: str) -> dict[str, str]:
        path = Path(file_path)

        if not path.exists():
            raise ConfigFileException(f"Unable to find properties file: {file_path}")

        properties: dict[str, str] = {}

        try:
            with path.open("r", encoding="utf-8") as file:
                for raw_line in file:
                    line = raw_line.strip()

                    if not line or line.startswith("#") or line.startswith("!"):
                        continue

                    if "=" in line:
                        key, value = line.split("=", 1)
                    elif ":" in line:
                        key, value = line.split(":", 1)
                    else:
                        key, value = line, ""

                    properties[key.strip()] = value.strip()

        except OSError as exc:
            raise ConfigFileException(f"Unable to load properties file: {file_path}") from exc

        return properties