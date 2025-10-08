from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

from database.models.wallet import Wallet, WalletStatus


class CRUDWallet:

    @staticmethod
    def create(db: Session, customer_user_id: int, private_key: str, public_key: str, received_amount: float,
               status: WalletStatus):
        db.add(Wallet(customer_user_id=customer_user_id, private_key=private_key, public_key=public_key,
                      received_amount=received_amount, status=status))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(Wallet).where(Wallet.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[Wallet]:
        statement = select(Wallet)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> Wallet | None:
        statement = select(Wallet).where(Wallet.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_customer_user_id(db: Session, customer_user_id: int) -> Sequence[Wallet]:
        statement = select(Wallet).where(Wallet.customer_user_id == customer_user_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_status(db: Session, status: WalletStatus) -> Sequence[Wallet]:
        statement = select(Wallet).where(Wallet.status == status)
        return db.execute(statement).scalars().all()

    @staticmethod
    def update_status(db: Session, id: int, new_status: WalletStatus):
        statement = update(Wallet).where(Wallet.id == id).values(status=new_status)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_received_amount(db: Session, id: int, new_amount: float):
        statement = update(Wallet).where(Wallet.id == id).values(received_amount=new_amount)
        db.execute(statement)
        db.commit()
