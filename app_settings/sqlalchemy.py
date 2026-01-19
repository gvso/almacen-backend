from typing import Any

from pydantic import Field, ValidationInfo, field_validator
from pydantic_settings import BaseSettings


class SQLAlchemySettings(BaseSettings):
    database_url: str = Field(default=..., alias="DATABASE_URL")
    database_url_test: str = Field(alias="DATABASE_URL_TEST", default="")
    statement_timeout: str = Field(default="10000", alias="SQLALCHEMY_STATEMENT_TIMEOUT")
    idle_in_transaction_session_timeout: str = Field(
        default="10000", alias="SQLALCHEMY_IDLE_IN_TRANSACTION_SESSION_TIMEOUT_MS"
    )
    engine_options: dict[str, Any] = {}

    @field_validator("engine_options")
    def create_engine_options(cls, v: Any, info: ValidationInfo) -> dict[str, Any]:
        database_url = info.data.get("database_url", "")

        # PgBouncer (used by fly.io managed Postgres) doesn't support
        # setting statement_timeout via connect_args
        if "pgbouncer" in database_url or "flympg.net" in database_url:
            return {}

        statement_timeout = f"statement_timeout={info.data['statement_timeout']}"
        idle_in_transaction_session_timeout = (
            f"idle_in_transaction_session_timeout={info.data['idle_in_transaction_session_timeout']}"
        )
        result = {
            "connect_args": {"options": f"-c {statement_timeout} -c {idle_in_transaction_session_timeout}"},
        }
        return result
