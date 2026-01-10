"""Default CRUD behaviour for models"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

import sqlalchemy as sa
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.orm import Mapped, Query, mapped_column
from typing_extensions import Self

from app.db import FlaskSQABaseModel, db


class BaseModel(FlaskSQABaseModel):
    __abstract__ = True

    __tablename__: str

    __hidden_columns__: list[str] = []

    query: Query[Self]

    def as_dict(
        self,
        levels: int = 1,
        current_level: int = 0,
        relationship: bool = False,
        relationships: list[str] | None = None,
    ) -> dict[str, Any]:
        # TODO: Deprecate relationship in favor of explicitly passing relationships to include.
        data: dict[str, Any] = {}
        for column in self.__table__.columns:
            if column.name in self.__hidden_columns__:
                continue

            raw_value = getattr(self, column.name)
            value = raw_value
            if isinstance(raw_value, datetime):
                value = raw_value.isoformat()
            if isinstance(raw_value, enum.Enum):
                value = raw_value.value
            if isinstance(raw_value, list):
                new_list = []
                for item in raw_value:
                    if isinstance(item, enum.Enum):
                        new_list.append(item.value)
                        continue
                    new_list.append(item)
                value = new_list
            if isinstance(raw_value, PydanticBaseModel):
                value = raw_value.model_dump()

            data[column.name] = value

        relationships = relationships or []
        if relationship is True or len(relationships) > 0:
            for name in self.__mapper__.relationships.keys():
                if len(relationships) > 0 and name not in relationships and "*" not in relationships:
                    continue
                rel: BaseModel | list[BaseModel] = getattr(self, name)
                if isinstance(rel, list):
                    if current_level < levels:
                        data[name] = [r.as_dict(current_level=current_level + 1) for r in rel]
                elif isinstance(rel, BaseModel):
                    if current_level < levels:
                        data[name] = rel.as_dict(current_level=current_level + 1)

        return data


class ModelWithId(BaseModel):
    __abstract__ = True

    # We're using ULIDs but storing them in a 128-bit UUID field.
    # Check https://blog.daveallie.com/ulid-primary-keys for reference.
    id: Mapped[int] = mapped_column(sa.BigInteger(), primary_key=True)


class ModelWithDates(BaseModel):
    __abstract__ = True

    inserted_at: Mapped[datetime] = mapped_column(sa.DateTime(), server_default=sa.text("now()"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(), server_default=sa.text("now()"), onupdate=db.func.now(), nullable=False
    )


class ModelWithCreatedBy(BaseModel):
    __abstract__ = True

    created_by_id: Mapped[uuid.UUID | None] = mapped_column(sa.UUID(), nullable=True)  # type: ignore


class SoftDeletable(BaseModel):
    __abstract__ = True

    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime())
