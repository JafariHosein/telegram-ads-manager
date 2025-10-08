from typing import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from database.models.session import Session as SessionModel


class CRUDSession:

    @staticmethod
    def create(db: Session, account_id: int, downloader_user_id: int, is_active: bool = True):
        db.add(SessionModel(account_id=account_id, downloader_user_id=downloader_user_id, is_active=is_active))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(SessionModel).where(SessionModel.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[SessionModel]:
        statement = select(SessionModel)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id) -> SessionModel | None:
        statement = select(SessionModel).where(SessionModel.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_account_id(db: Session, account_id: int, is_active: bool = True) -> Sequence[SessionModel]:
        statement = select(SessionModel).where(SessionModel.account_id == account_id, SessionModel.is_active == is_active)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_downloader_user_id(db: Session, downloader_user_id: int, is_active: bool = True) -> Sequence[SessionModel]:
        statement = select(SessionModel).where(SessionModel.downloader_user_id == downloader_user_id, SessionModel.is_active == is_active)
        return db.execute(statement).scalars().all()

    @staticmethod
    def deactivate(db: Session, account_id: int):
        statement = update(SessionModel).where(SessionModel.account_id == account_id).values(is_active=False)
        db.execute(statement)
        db.commit()
