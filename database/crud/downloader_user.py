from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

from database.models.downloader_user import DownloaderUser


class CRUDDownloaderUser:

    @staticmethod
    def create(db: Session, chat_id: str, state: str = None, state_data: str = None,
               bot_last_message_id: int = None):
        db.add(DownloaderUser(chat_id=chat_id, state=state, state_data=state_data,
                              bot_last_message_id=bot_last_message_id))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(DownloaderUser).where(DownloaderUser.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[DownloaderUser]:
        statement = select(DownloaderUser)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> DownloaderUser | None:
        statement = select(DownloaderUser).where(DownloaderUser.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_chat_id(db: Session, chat_id: str) -> DownloaderUser | None:
        statement = select(DownloaderUser).where(DownloaderUser.chat_id == chat_id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def update_state(db: Session, chat_id: str, new_state: str):
        statement = update(DownloaderUser).where(DownloaderUser.chat_id == chat_id).values(state=new_state)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_bot_last_message_id(db: Session, chat_id: str, new_bot_lst_msg_id: int):
        statement = update(DownloaderUser).where(DownloaderUser.chat_id == chat_id).values(bot_last_message_id=new_bot_lst_msg_id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_state_data(db: Session, chat_id: str, new_state_data: str):
        statement = update(DownloaderUser).where(DownloaderUser.chat_id == chat_id).values(state_data=new_state_data)
        db.execute(statement)
        db.commit()
