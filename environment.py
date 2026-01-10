from enum import Enum


class Environment(Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    QA = "qa"
    PRODUCTION = "production"
