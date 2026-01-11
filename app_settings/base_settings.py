from pydantic import Field
from pydantic_settings import BaseSettings

from environment import Environment

from .google import GoogleCloudSettings
from .gunicorn import GunicornSettings
from .log import LoggingSettings
from .sqlalchemy import SQLAlchemySettings


class Settings(BaseSettings):
    admin_password: str = Field(alias="ADMIN_PASSWORD")
    session_key: str = Field(alias="FLASK_SESSION_KEY")
    environment: Environment = Field(alias="ENVIRONMENT")

    google: GoogleCloudSettings = Field(GoogleCloudSettings())
    gunicorn: GunicornSettings = Field(GunicornSettings())
    logging: LoggingSettings = Field(LoggingSettings())
    sqlalchemy: SQLAlchemySettings = Field(SQLAlchemySettings())
