from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

from database.models.transfer_request import TransferRequest, TransferRequestStatus


class CRUDTransferRequest:

    @staticmethod
    def create(db: Session, account_id: int, target_account_id: int, amount: int,
               auto_completed: bool, reason: str = None, status: TransferRequestStatus = TransferRequestStatus.PENDING):
        db.add(TransferRequest(account_id=account_id, target_account_id=target_account_id, amount=amount,
                               auto_completed=auto_completed, reason=reason, status=status))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(TransferRequest).where(TransferRequest.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[TransferRequest]:
        statement = select(TransferRequest)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_account_id(db: Session, account_id: int, status: TransferRequestStatus = None) -> Sequence[TransferRequest]:
        if status:
            statement = select(TransferRequest).where(TransferRequest.account_id == account_id,TransferRequest.status == status)
        else:
            statement = select(TransferRequest).where(TransferRequest.account_id == account_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> TransferRequest | None:
        statement = select(TransferRequest).where(TransferRequest.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_status(db: Session, status: TransferRequestStatus) -> Sequence[TransferRequest]:
        statement = select(TransferRequest).where(TransferRequest.status == status)
        return db.execute(statement).scalars().all()

    @staticmethod
    def update_status(db: Session, id: int, new_status: TransferRequestStatus):
        statement = update(TransferRequest).where(TransferRequest.id == id).values(status=new_status)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_reason(db: Session, id: int, new_reason: str):
        statement = update(TransferRequest).where(TransferRequest.id == id).values(reason=new_reason)
        db.execute(statement)
        db.commit()
