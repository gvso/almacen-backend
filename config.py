import gunicorn
from dotenv import load_dotenv

load_dotenv()

from app_settings import settings

# NOTE: gunicorn configs get picked up if they are set globally in our config file
bind = f"""[::]:{settings.gunicorn.port}"""
workers = settings.gunicorn.num_workers
threads = settings.gunicorn.num_threads
timeout = settings.gunicorn.timeout
worker_tmp_dir = settings.gunicorn.worker_tmp_dir
loglevel = settings.gunicorn.loglevel
gunicorn.SERVER_SOFTWARE = "Quinta Server"
accesslog = "-"
