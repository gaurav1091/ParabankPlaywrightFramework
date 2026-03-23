from enum import Enum


class EnvironmentType(str, Enum):
    QA = "qa"
    STAGE = "stage"
    DEV = "dev"