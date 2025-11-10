from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

from database.models.downloader_user import DownloaderUser
from database.crud.manager import UpdateType


class CRUDDownloaderUser:

    @staticmethod
    def create(db: Session, chat_id: str, state: str = "", state_data: str = "",
               bot_last_message_id: int = None, can_use_bot=True, captcha_failures: int = 0):
        db.add(DownloaderUser(chat_id=chat_id, state=state, state_data=state_data,
                              bot_last_message_id=bot_last_message_id, can_use_bot=can_use_bot, captcha_failures=captcha_failures))
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
    def get_block_list(db: Session) -> Sequence[DownloaderUser]:
        statement = select(DownloaderUser).where(DownloaderUser.can_use_bot == False)
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

    @staticmethod
    def update_can_use_bot(db: Session, chat_id: str, new_can_use_bot: bool):
        statement = update(DownloaderUser).where(DownloaderUser.chat_id == chat_id).values(can_use_bot=new_can_use_bot)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_captcha_failures(db: Session, chat_id: str, update_type: UpdateType, value: int):
        if update_type == UpdateType.NORMAL:
            statement = update(DownloaderUser).where(DownloaderUser.chat_id == chat_id).values(captcha_failures=value)
        elif update_type == UpdateType.INCREMENT:
            statement = update(DownloaderUser).where(DownloaderUser.chat_id == chat_id).values(captcha_failures=DownloaderUser.captcha_failures + value)
        else:
            statement = update(DownloaderUser).where(DownloaderUser.chat_id == chat_id).values(captcha_failures=DownloaderUser.captcha_failures - value)

        db.execute(statement)
        db.commit()
