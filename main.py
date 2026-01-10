from dotenv import load_dotenv

from app.container import get_wire_container
from app.create_app import create_app
from logging_config import setup_logging

load_dotenv(override=True)

setup_logging()
container = get_wire_container()
app = create_app()
