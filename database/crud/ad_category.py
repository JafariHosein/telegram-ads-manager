from typing import Sequence

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update, func, cast

from database.models.ad_category import AdCategory


class CRUDAdCategory:

    @staticmethod
    def create(db: Session, title: str, min_rate: int):
        db.add(AdCategory(title=title, min_rate=min_rate))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(AdCategory).where(AdCategory.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def delete_by_title(db: Session, title: str):
        statement = select(AdCategory).where(AdCategory.title == title)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[AdCategory]:
        statement = select(AdCategory)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> AdCategory | None:
        statement = select(AdCategory).where(AdCategory.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_title(db: Session, title: str) -> AdCategory | None:
        statement = select(AdCategory).where(AdCategory.title == title)
        return db.execute(statement).scalars().first()
