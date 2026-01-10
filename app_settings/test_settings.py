import logging
import os
from unittest.mock import Mock

from environment import Environment


class TestSettings(Mock):
    environment = Environment.TEST
    session_key = "test"
    jwt_key = "test"
    logging = Mock(level=logging.INFO, use_config=True)
    sqlalchemy = Mock(
        database_url=(
            "postgresql://local_db_user:local_db_password@postgres:5432/vincula_tests_"
            f"{os.getenv('PYTEST_XDIST_WORKER', 'master')}"
        ),
        database_url_test=(
            "postgresql://local_db_user:local_db_password@postgres:5432/vincula_tests_"
            f"{os.getenv('PYTEST_XDIST_WORKER', 'master')}"
        ),
        engine_options={},
    )
