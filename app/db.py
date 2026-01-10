import logging

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import select, text

from app_settings import settings


class FlaskSQABaseModel(DeclarativeBase):
    pass


logger = logging.getLogger(__name__)

db = SQLAlchemy(model_class=FlaskSQABaseModel, engine_options=settings.sqlalchemy.engine_options)


def reconnect_db(db: SQLAlchemy) -> None:
    try:
        db.session.execute(select(text("1"))).all()
    except DatabaseError:
        logger.warning("Database connection lost. Trying to reconnect...")
        db.session.rollback()
        db.session.close()
    except Exception:
        logger.warning("Database connection lost. Trying to reconnect...", stack_info=True)
        db.session.rollback()
        db.session.close()
