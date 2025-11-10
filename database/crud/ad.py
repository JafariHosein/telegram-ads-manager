import random
from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update, desc

from database.models.ad import Ad, AdLinkType, AdChannelType, AdStatus


class CRUDAd:

    @staticmethod
    def __generate_unique_random_id(db: Session):
        while True:
            rand_id = random.randint(10000, 999999)
            exists = db.query(Ad).filter_by(id=rand_id).first()
            if not exists:
                return rand_id

    @staticmethod
    def create(db: Session, channel_chat_id: str, channel_name: str, channel_type: AdChannelType,
               description: str, rate: int, capacity: int, auto_complete: bool, category_title: str, channel_link: str,
               prize: dict = None, channel_username: str = None, ad_link_type: AdLinkType = AdLinkType.NORMAL,
               customer_user_id: int = None, status: AdStatus = AdStatus.ACTIVE) -> int:
        new_ad = Ad(id=CRUDAd.__generate_unique_random_id(db), customer_user_id=customer_user_id, channel_chat_id=channel_chat_id, channel_name=channel_name, channel_type=channel_type,
                    description=description, rate=rate, capacity=capacity, auto_complete=auto_complete, category_title=category_title,
                    prize=prize, channel_username=channel_username, status=status, link_type=ad_link_type, channel_link=channel_link)
        db.add(new_ad)
        db.commit()
        db.refresh(new_ad)

        from utils.logger import Logger
        Logger.notice("تبلیغ شماره " + f"{new_ad.id} ساخته شد")

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
    def get_by_channel_chat_id(db: Session, chat_id: str, status: AdStatus = None) -> Sequence[Ad]:
        if status:
            statement = select(Ad).where(Ad.channel_chat_id == chat_id, Ad.status == status)
        else:
            statement = select(Ad).where(Ad.channel_chat_id == chat_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_title(db: Session, title: str, status: AdStatus = None) -> Sequence[Ad]:
        if status:
            statement = select(Ad).where(Ad.category_title == title, Ad.status == status).order_by(Ad.created_at.desc())
        else:
            statement = select(Ad).where(Ad.category_title == title).order_by(Ad.created_at.desc())
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_customer_user_id(db: Session, customer_user_id: int) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.customer_user_id == customer_user_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_category_title(db: Session, category_title: str) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.category_title == category_title)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_actives(db: Session) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.status == AdStatus.ACTIVE)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_inactives(db: Session) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.status == AdStatus.INACTIVE)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_completed(db: Session) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.status == AdStatus.COMPLETED)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_unverifies(db: Session) -> Sequence[Ad]:
        statement = select(Ad).where(Ad.status == AdStatus.UNVERIFIED)
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
    def update_status(db: Session, id: int, new_status: AdStatus):
        statement = update(Ad).where(Ad.id == id).values(status=new_status)
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
