import random
from typing import Sequence

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update, func, cast

from database.models.account import Account, AccountRole, AccountStatus
from database.crud.manager import UpdateType



class CRUDAccount:

    @staticmethod
    def __generate_unique_random_id(db:Session):
        while True:
            rand_id = random.randint(10000, 999999)
            exists = db.query(Account).filter_by(id=rand_id).first()
            if not exists:
                return rand_id

    @staticmethod
    def create(db: Session, username: str, password: str, status: AccountStatus = AccountStatus.ACTIVE,
               role: AccountRole = AccountRole.DOWNLOADER, ad_ids: list[int] = None, linked_username: dict = None, balance: int = 0) -> int:
        new_account = Account(id=CRUDAccount.__generate_unique_random_id(db),balance=balance, username=username, password=password, status=status, role=role, ad_ids=ad_ids,
                              linked_username=linked_username)
        db.add(new_account)
        db.commit()
        db.refresh(new_account)

        from utils.logger import Logger
        Logger.notice("اکانت شماره " + f"{new_account.id} ساخته شد" + "\n\n" + "توسط " + username)

        return new_account.id

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(Account).where(Account.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[Account]:
        statement = select(Account)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> Account | None:
        statement = select(Account).where(Account.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Account | None:
        statement = select(Account).where(Account.username == username)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_role(db: Session, role: AccountRole) -> Sequence[Account]:
        statement = select(Account).where(Account.role == role)
        return db.execute(statement).scalars().all()

    @staticmethod
    def username_exist(db: Session, username: str) -> bool:
        statement = select(Account).where(Account.username == username)
        return bool(db.execute(statement).scalars().first())

    @staticmethod
    def update_balance(db: Session, id: int, update_type: UpdateType, new_balance: int):
        if update_type == UpdateType.NORMAL:
            statement = update(Account).where(Account.id == id).values(balance=new_balance)
        elif update_type == UpdateType.DECREMENT:
            statement = update(Account).where(Account.id == id).values(balance=Account.balance - new_balance)
        else:
            statement = update(Account).where(Account.id == id).values(balance=Account.balance + new_balance)

        db.execute(statement)
        db.commit()

    @staticmethod
    def update_password(db: Session, id: int, new_password: str):
        statement = update(Account).where(Account.id == id).values(password=new_password)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_status(db: Session, id: int, new_status: AccountStatus):
        statement = update(Account).where(Account.id == id).values(status=new_status)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_role(db: Session, id: int, new_role: AccountRole):
        statement = update(Account).where(Account.id == id).values(role=new_role)
        db.execute(statement)
        db.commit()

    @staticmethod
    def add_id(db: Session, id: int, ad_id: int):
        statement = update(Account).where(Account.id == id).values(ad_ids=func.array_append(Account.ad_ids, ad_id))
        db.execute(statement)
        db.commit()

    @staticmethod
    def remove_id(db: Session, id: int, ad_id: int):
        statement = update(Account).where(Account.id == id).values(ad_ids=func.array_remove(Account.ad_ids, ad_id))
        db.execute(statement)
        db.commit()

    @staticmethod
    def add_linked_username(db: Session, id: int, new_linked_username: dict):
        statement = update(Account).where(Account.id == id).values(linked_username=Account.linked_username.op("||")(cast(new_linked_username, JSONB)))
        db.execute(statement)
        db.commit()

    @staticmethod
    def remove_linked_username(db: Session, id: int, linked_username_key: str):
        statement = update(Account).where(Account.id == id).values(linked_username=Account.linked_username - linked_username_key)
        db.execute(statement)
        db.commit()

    @staticmethod
    def login(db: Session, username: str, password: str) -> tuple[bool, int]:
        statement = select(Account).where(Account.username == username)
        result = db.execute(statement).scalars().first()
        if result:
            import bcrypt
            is_correct = bcrypt.checkpw(password.encode("utf-8"), result.password.encode("utf-8"))
            return is_correct, result.id
        return False, None
