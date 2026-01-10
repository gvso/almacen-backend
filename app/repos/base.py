import logging
from datetime import datetime
from typing import Any, Generator, Generic, Mapping, TypeVar
from uuid import UUID

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Column
from sqlalchemy.orm import Query
from sqlalchemy.orm.attributes import flag_modified

from app.db import db
from app.exceptions import EntityNotFoundError
from app.models.base import BaseModel, SoftDeletable

ModelT = TypeVar("ModelT", bound=BaseModel)


class Repo(Generic[ModelT]):
    def __init__(self, model: type[ModelT]) -> None:
        self._logger = logging.getLogger(__name__)
        self.session = db.session
        self.model = model

    def get_query(self) -> Query[ModelT]:
        return self.session.query(self.model)

    def get(self, primary_key: UUID | str) -> ModelT | None:
        """Gets entity by primary key"""
        return self.session.get(self.model, primary_key)

    def get_or_fail(self, primary_key: UUID) -> ModelT:
        obj = self.get(primary_key)
        if obj is None:
            raise EntityNotFoundError(f"{self.model.__tablename__} with id {primary_key} not found")
        return obj

    def get_in_batch(
        self, query: Query[ModelT], batch_number: int = 500, sort_column_name: str = "id"
    ) -> Generator[Query[ModelT], None, None]:
        sort_column: Column[Any] = getattr(self.model, sort_column_name)
        last_item = query.order_by(sort_column.desc()).first()
        last_id = getattr(last_item, sort_column_name, None) if last_item else None

        query = query.order_by(sort_column.asc())
        i = None
        while True:
            # If it's the first batch, filter greater than None.
            if i is None:
                records = query.filter(sort_column <= last_id).limit(batch_number)
            else:
                records = query.filter(sort_column > i, sort_column <= last_id).limit(batch_number)

            batch_records = records.all()
            if not batch_records:
                break

            yield records
            # Set i to the last record's sort_column value in the current batch
            i = getattr(batch_records[-1], sort_column_name)
            self.commit()

    def update(self, base_obj: ModelT, update_data: Mapping[str, Any], do_commit: bool = True) -> ModelT:
        for key, value in update_data.items():
            if isinstance(value, dict) or isinstance(value, PydanticBaseModel):
                # Needs to flag when updating a JSON field.
                self._logger.debug(f"Flagging that key '{key}' has been updated for entity {base_obj}")
                flag_modified(base_obj, key)
            setattr(base_obj, key, value)
        if do_commit:
            self.session.commit()
        return base_obj

    def remove(self, one_or_multiple: ModelT | list[ModelT], do_commit: bool = True, hard_delete: bool = False) -> None:
        objects = one_or_multiple if isinstance(one_or_multiple, list) else [one_or_multiple]
        if not objects:
            return
        for obj in objects:
            if isinstance(obj, SoftDeletable) and hard_delete is False:
                self.update(obj, {"deleted_at": datetime.now()}, do_commit)  # type: ignore
            else:
                self.session.delete(obj)
        if do_commit:
            self.commit()
        else:
            self.session.flush()

    def add(self, object: ModelT) -> ModelT:
        return self.persist_all([object], do_commit=False)[0]

    def add_all(self, objects: list[ModelT]) -> list[ModelT]:
        return self.persist_all(objects, do_commit=False)

    def persist(self, object: ModelT, do_commit: bool = True) -> ModelT:
        return self.persist_all([object], do_commit)[0]

    def persist_all(self, objects: list[ModelT], do_commit: bool = True) -> list[ModelT]:
        self.session.add_all(objects)
        if do_commit:
            self.commit()
        else:
            self.session.flush()
        return objects

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
