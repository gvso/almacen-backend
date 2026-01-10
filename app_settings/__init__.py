import os
from typing import TYPE_CHECKING, cast

from pydantic_settings import BaseSettings


def get_settings() -> BaseSettings:
    if os.getenv("APP_ENV") == "test":
        from .test_settings import TestSettings

        return TestSettings()

    from .base_settings import Settings

    return Settings()  # type: ignore


if TYPE_CHECKING:
    from .base_settings import Settings

    settings = cast(Settings, get_settings())
else:
    settings = get_settings()
