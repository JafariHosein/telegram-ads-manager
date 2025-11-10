from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

from database.models.payout_request import PayoutRequestStatus, PayoutRequestType, PayoutRequest, PayoutRequestDestinationType


class CRUDPayoutRequest:

    @staticmethod
    def create(db: Session, account_id: int, type: PayoutRequestType, destination: PayoutRequestDestinationType,
               auto_complete: bool, amount: int, status: PayoutRequestStatus = PayoutRequestStatus.PENDING,
               wallet_address: str = None, bank_id: int = None, reason: str = None):
        db.add(PayoutRequest(account_id=account_id, type=type, destination_type=destination,
                             amount=amount, status=status, wallet_address=wallet_address, auto_complete=auto_complete,
                             bank_id=bank_id, reason=reason))

        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(PayoutRequest).where(PayoutRequest.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[PayoutRequest]:
        statement = select(PayoutRequest)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> PayoutRequest | None:
        statement = select(PayoutRequest).where(PayoutRequest.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_account_id(db: Session, account_id: int, status: PayoutRequestStatus = None) -> Sequence[PayoutRequest]:
        if status:
            statement = select(PayoutRequest).where(PayoutRequest.account_id == account_id, PayoutRequest.status == status)
        else:
            statement = select(PayoutRequest).where(PayoutRequest.account_id == account_id).order_by(PayoutRequest.created_at.desc())
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_bank_id(db: Session, bank_id: int) -> Sequence[PayoutRequest]:
        statement = select(PayoutRequest).where(PayoutRequest.bank_id == bank_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_status(db: Session, status=PayoutRequestStatus) -> Sequence[PayoutRequest]:
        statement = select(PayoutRequest).where(PayoutRequest.status == status)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_type(db: Session, type: PayoutRequestType) -> Sequence[PayoutRequest]:
        statement = select(PayoutRequest).where(PayoutRequest.type == type)
        return db.execute(statement).scalars().all()

    @staticmethod
    def update_status(db: Session, id: int, new_status: PayoutRequestStatus):
        statement = update(PayoutRequest).where(PayoutRequest.id == id).values(status=new_status)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_reason(db: Session, id: int, new_reason: str):
        statement = update(PayoutRequest).where(PayoutRequest.id == id).values(reason=new_reason)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_auto_complete(db: Session, id: int, auto_complete: bool):
        statement = update(PayoutRequest).where(PayoutRequest.id == id).values(auto_complete=auto_complete)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_transaction_url(db: Session, id: int, transaction_url: str):
        statement = update(PayoutRequest).where(PayoutRequest.id == id).values(transaction_url=transaction_url)
        db.execute(statement)
        db.commit()
