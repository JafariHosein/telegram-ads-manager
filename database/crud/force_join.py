from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select

from database.models.force_join import ForceJoin


class CRUDForceJoin:

    @staticmethod
    def create(db: Session, chat_id: str, username: str):
        db.add(ForceJoin(chat_id=chat_id, username=username))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(ForceJoin).where(ForceJoin.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[ForceJoin]:
        statement = select(ForceJoin)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> ForceJoin | None:
        statement = select(ForceJoin).where(ForceJoin.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def exists(db: Session, username: str) -> bool:
        statement = select(ForceJoin).where(ForceJoin.username == username)
        return bool(db.execute(statement).scalars().first())
