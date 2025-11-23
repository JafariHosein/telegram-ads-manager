from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select

from database.models.bank_account import BankAccount, BankAccountType


class CRUDBankAccount:

    @staticmethod
    def create(db: Session, account_id: int, type: BankAccountType, value: str, full_name: str):
        db.add(BankAccount(account_id=account_id, type=type, value=value, full_name=full_name))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(BankAccount).where(BankAccount.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[BankAccount]:
        statement = select(BankAccount)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> BankAccount | None:
        statement = select(BankAccount).where(BankAccount.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_value(db: Session, account_id: int, value: str) -> BankAccount | None:
        statement = select(BankAccount).where(BankAccount.account_id == account_id, BankAccount.value == value)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_account_id(db: Session, account_id: int) -> Sequence[BankAccount]:
        statement = select(BankAccount).where(BankAccount.account_id == account_id)
        return db.execute(statement).scalars().all()
