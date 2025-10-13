from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

from database.models.register_request import RegisterRequest, RegisterRequestStatus


class CRUDRegisterRequest:

    @staticmethod
    def create(db: Session, linked_username: dict, downloader_user_id: int, reason: str = None,
               status: RegisterRequestStatus = RegisterRequestStatus.PENDING):
        db.add(RegisterRequest(linked_username=linked_username, status=status, reason=reason,
                               downloader_user_id=downloader_user_id))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(RegisterRequest).where(RegisterRequest.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[RegisterRequest]:
        statement = select(RegisterRequest)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> RegisterRequest | None:
        statement = select(RegisterRequest).where(RegisterRequest.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_status(db: Session, status: RegisterRequestStatus) -> Sequence[RegisterRequest]:
        statement = select(RegisterRequest).where(RegisterRequest.status == status)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_status_and_downloader_user_id(db: Session, downloader_user_id: int, status: RegisterRequestStatus) -> Sequence[RegisterRequest]:
        statement = select(RegisterRequest).where(RegisterRequest.status == status, RegisterRequest.downloader_user_id == downloader_user_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def update_status(db: Session, id: int, new_status: RegisterRequestStatus):
        statement = update(RegisterRequest).where(RegisterRequest.id == id).values(status=new_status)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_reason(db: Session, id: int, new_reason: str):
        statement = update(RegisterRequest).where(RegisterRequest.id == id).values(reason=new_reason)
        db.execute(statement)
        db.commit()
