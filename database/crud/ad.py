from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update

from database.models.ad import Ad, AdLinkType, AdChannelType


class CRUDAd:

    @staticmethod
    def create(db: Session, channel_chat_id: str, channel_name: str, channel_type: AdChannelType,
               description: str, rate: int, capacity: int, auto_complete: bool, category_title: str,
               prize: dict = None, is_active: bool = True, channel_username: str = None, is_verified: bool = False, ad_link_type: AdLinkType = AdLinkType.NORMAL,
               customer_user_id: int = None) -> int:
        new_ad = Ad(customer_user_id=customer_user_id, channel_chat_id=channel_chat_id, channel_name=channel_name, channel_type=channel_type,
                    description=description, rate=rate, capacity=capacity, auto_complete=auto_complete, category_title=category_title,
                    prize=prize, is_active=is_active, channel_username=channel_username, is_verified=is_verified, link_type=ad_link_type)
        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)

        return new_ad.id

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(Ad).where(Ad.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[Ad]:
        statement = select(Ad)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> Ad | None:
        statement = select(Ad).where(Ad.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_customer_user_id(db: Session, customer_user_id: int) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.customer_user_id == customer_user_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_category_title(db: Session, category_title: str) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.category_title == category_title)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_is_active(db: Session) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.is_active == True, Ad.is_completed == False)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_is_verified(db: Session) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.is_verified == True)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_is_not_verified(db: Session) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.is_completed == True, Ad.is_verified == False)
        return db.execute(statement).scalars().all()

    @staticmethod
    def update_description(db: Session, id: int, new_description: str):
        statement = update(Ad).where(Ad.id == id).values(description=new_description)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_capacity(db: Session, id: int, new_capacity: int):
        statement = update(Ad).where(Ad.id == id).values(capacity=new_capacity)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_auto_complete(db: Session, id: int, new_auto_complete: bool):
        statement = update(Ad).where(Ad.id == id).values(auto_complete=new_auto_complete)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_is_active(db: Session, id: int, is_active: bool):
        statement = update(Ad).where(Ad.id == id).values(is_active=is_active)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_is_verified(db: Session, id: int, is_verified: bool):
        statement = update(Ad).where(Ad.id == id).values(is_verified=is_verified)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_is_completed(db: Session, id: int, is_completed: bool):
        statement = update(Ad).where(Ad.id == id).values(is_completed=is_completed)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_prize(db: Session, id: int, prize: dict):
        statement = update(Ad).where(Ad.id == id).values(prize=prize)
        db.execute(statement)
        db.commit()

    @staticmethod
    def update_rate(db: Session, id: int, new_rate: int):
        statement = update(Ad).where(Ad.id == id).values(rate=new_rate)
        db.execute(statement)
        db.commit()
