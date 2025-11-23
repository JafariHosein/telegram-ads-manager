from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

from database.models.ad_request import AdRequest, AdRequestStatus, AdRequestChannelType


class CRUDAdRequest:

    @staticmethod
    def create(db: Session, customer_user_id: int, channel_chat_id: str, channel_name: str, channel_type: AdRequestChannelType,
               rate: int, capacity: int,  price_without_fee: int, final_price: int,
               status: AdRequestStatus = AdRequestStatus.PENDING, description: str = None, channel_username: str = None,
               reason: str = None):
        db.add(AdRequest(customer_user_id=customer_user_id, channel_chat_id=channel_chat_id, channel_name=channel_name,
                         channel_type=channel_type, rate=rate, capacity=capacity,
                         price_without_fee=price_without_fee, final_price=final_price, status=status,
                         description=description, channel_username=channel_username, reason=reason))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(AdRequest).where(AdRequest.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[AdRequest]:
        statement = select(AdRequest)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> AdRequest | None:
        statement = select(AdRequest).where(AdRequest.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_status(db: Session, status: AdRequestStatus) -> Sequence[AdRequest]:
        statement = select(AdRequest).where(AdRequest.status == status)
        return db.execute(statement).scalars().all()

    @staticmethod
    def update_status(db: Session, id: int, new_status: AdRequestStatus):
        statement = update(AdRequest).where(AdRequest.id == id).values(status=new_status)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_reason(db: Session, id: int, new_reason: str):
        statement = update(AdRequest).where(AdRequest.id == id).values(reason=new_reason)
        db.execute(statement)
        db.commit()
