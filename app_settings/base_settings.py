from pydantic import Field
from pydantic_settings import BaseSettings

from environment import Environment

from .gunicorn import GunicornSettings
from .log import LoggingSettings
from .sqlalchemy import SQLAlchemySettings


class Settings(BaseSettings):
    session_key: str = Field(alias="FLASK_SESSION_KEY")
    environment: Environment = Field(alias="ENVIRONMENT")

    gunicorn: GunicornSettings = Field(GunicornSettings())
    logging: LoggingSettings = Field(LoggingSettings())
    sqlalchemy: SQLAlchemySettings = Field(SQLAlchemySettings())
