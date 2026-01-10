from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class GunicornSettings(BaseSettings):
    loglevel: str = Field(default=..., alias="GUNICORN_LOGLEVEL")
    port: int = Field(default=..., alias="GUNICORN_PORT")
    num_threads: int = Field(default=..., alias="GUNICORN_NUM_THREADS")
    num_workers: int = Field(default=..., alias="GUNICORN_NUM_WORKERS")
    timeout: str = Field(default=..., alias="GUNICORN_TIMEOUT")
    worker_tmp_dir: str = Field(default=..., alias="GUNICORN_WORKER_DIR")

    @field_validator("loglevel", mode="before")
    def set_logging_level(cls, level: str) -> str:
        return level.lower()
