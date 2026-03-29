from pathlib import Path


class ReportPathManager:
    @staticmethod
    def create_directory_if_not_exists(directory_path: str) -> None:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
