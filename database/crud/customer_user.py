from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

from database.models.customer_user import CustomerUser
from database.crud.manager import UpdateBalanceType


class CRUDCustomerUser:

    @staticmethod
    def create(db: Session, chat_id: str, state: str = None, state_data: str = None,
               balance: int = 0, bot_last_message_id: int = None):
        db.add(CustomerUser(chat_id=chat_id, state=state, state_data=state_data,
                            balance=balance, bot_last_message_id=bot_last_message_id))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(CustomerUser).where(CustomerUser.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[CustomerUser]:
        statement = select(CustomerUser)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> CustomerUser | None:
        statement = select(CustomerUser).where(CustomerUser.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_chat_id(db: Session, chat_id: str) -> CustomerUser | None:
        statement = select(CustomerUser).where(CustomerUser.chat_id == chat_id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def update_balance(db: Session, id: int, balance_type: UpdateBalanceType, new_balance: int):
        if balance_type == UpdateBalanceType.NORMAL:
            statement = update(CustomerUser).where(CustomerUser.id == id).values(balance=new_balance)
        elif balance_type == UpdateBalanceType.INCREMENT:
            statement = update(CustomerUser).where(CustomerUser.id == id).values(balance=CustomerUser.balance + new_balance)
        else:
            statement = update(CustomerUser).where(CustomerUser.id == id).values(balance=CustomerUser.balance - new_balance)

        db.execute(statement)
        db.commit()

    @staticmethod
    def update_state(db: Session, id: int, new_state: str):
        statement = update(CustomerUser).where(CustomerUser.id == id).values(state=new_state)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_bot_last_message_id(db: Session, id: int, new_bot_lst_msg_id: int):
        statement = update(CustomerUser).where(CustomerUser.id == id).values(bot_last_message_id=new_bot_lst_msg_id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_state_data(db: Session, id: int, new_state_data: str):
        statement = update(CustomerUser).where(CustomerUser.id == id).values(state_data=new_state_data)
        db.execute(statement)
        db.commit()
