from typing import Sequence

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update, cast

from database.models.link import Link


class CRUDLink:

    @staticmethod
    def create(db: Session, account_id: int, ad_id: int, url: str, is_request_type: bool, members: dict = None,
               point: float = 0, count: int = 0):
        db.add(Link(account_id=account_id, ad_id=ad_id, url=url, is_request_type=is_request_type,
                    members=members, point=point, count=count))
        db.commit()

    @staticmethod
    def delete(db: Session, id: int):
        statement = delete(Link).where(Link.id == id)
        db.execute(statement)
        db.commit()

    @staticmethod
    def get_all(db: Session) -> Sequence[Link]:
        statement = select(Link)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_id(db: Session, id: int) -> Link | None:
        statement = select(Link).where(Link.id == id)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_account_id(db: Session, account_id: int) -> Sequence[Link]:
        statement = select(Link).where(Link.account_id == account_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_url(db: Session, url: str) -> Link | None:
        statement = select(Link).where(Link.url == url)
        return db.execute(statement).scalars().first()

    @staticmethod
    def get_by_ad_id(db: Session, ad_id: int) -> Sequence[Link]:
        statement = select(Link).where(Link.ad_id == ad_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def add_member(db: Session, id: int, new_member: dict):
        statement = update(Link).where(Link.id == id).values(members=Link.members.op("||")(cast(new_member, JSONB)))
        db.execute(statement)
        db.commit()

        CRUDLink.__increase_count(db, id, 1)
        CRUDLink.__calculate_point(db, id)

    @staticmethod
    def remove_member(db: Session, id: int, member: str):
        statement = update(Link).where(Link.id == id).values(members=Link.members - member)
        db.execute(statement)
        db.commit()

        CRUDLink.__decrease_count(db, id, 1)
        CRUDLink.__calculate_point(db, id)

    @staticmethod
    def __increase_count(db: Session, id: int, value: int = 1):
        statement = update(Link).where(Link.id == id).values(count=Link.count + value)
        db.execute(statement)
        db.commit()

    @staticmethod
    def __decrease_count(db: Session, id: int, value: int = 1):
        statement = update(Link).where(Link.id == id).values(count=Link.count - value)
        db.execute(statement)
        db.commit()

    @staticmethod
    def __calculate_point(db: Session, id: int):
        statement = select(Link).where(Link.id == id)
        data: Link = db.execute(statement).scalars().first()

        if not data:
            return

        if data.count == 0:
            statement = update(Link).where(Link.id == id).values(point=0)
        else:
            total_score = 0
            for chat_id, li in data.members.items():
                total_score += li[1]

            point = total_score / data.count

            statement = update(Link).where(Link.id == id).values(point=point)

        db.execute(statement)
        db.commit()
