from typing import Sequence

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session
from sqlalchemy import delete, select, update, cast, JSON, desc

from database.models.link import Link
from database.crud.ad import CRUDAd, AdStatus


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
    def get_top_20_by_ad_id(db: Session, ad_id: int) -> Sequence[Link]:
        statement = select(Link).where(Link.ad_id == ad_id, Link.count > 0).order_by(desc(Link.count)).limit(20)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_top_by_ad_id(db: Session, ad_id: int, limit: int) -> Sequence[Link]:
        statement = select(Link).where(Link.ad_id == ad_id, Link.count > 0).order_by(desc(Link.count)).limit(limit)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_by_ad_id(db: Session, ad_id: int) -> Sequence[Link]:
        statement = select(Link).where(Link.ad_id == ad_id)
        return db.execute(statement).scalars().all()

    @staticmethod
    def get_count_by_ad_id(db: Session, ad_id: int) -> int:
        statement = select(Link).where(Link.ad_id == ad_id)
        data = db.execute(statement).scalars().all()

        count = 0
        for link in data:
            count += link.count

        return count

    @staticmethod
    def exist(db: Session, ad_id: int, account_id: int) -> bool:
        statement = select(Link).where(Link.ad_id == ad_id, Link.account_id == account_id)
        return bool(db.execute(statement).scalars().all())

    @staticmethod
    def add_member(db: Session, id: int, new_member: dict):

        link = CRUDLink.get_by_id(db, id)
        ad = CRUDAd.get_by_id(db, link.ad_id)

        if ad.status != AdStatus.ACTIVE:
            return

        if not link.members:
            statement = update(Link).where(Link.id == id).values(members=new_member)
        else:
            statement = update(Link).where(Link.id == id).values(members=Link.members.op("||")(cast(new_member, JSONB)))
        db.execute(statement)
        db.commit()

        CRUDLink.__set_count(db, link_id=id)
        CRUDLink.__calculate_point(db, id=id)

    @staticmethod
    def remove_member(db: Session, ad_id: int, member: str):

        ad = CRUDAd.get_by_id(db, ad_id)

        if ad.status != AdStatus.ACTIVE:
            return

        links = db.query(Link).filter_by(ad_id=ad_id).all()

        if not links:
            return

        for link in links:
            members = link.members or {}
            if not isinstance(members, dict):
                members = {}

            members.pop(str(member), None)

            stmt = (
                update(Link)
                .where(Link.id == link.id)
                .values(
                    members=members
                )
            )
            db.execute(stmt)
            db.commit()

        CRUDLink.__set_count(db, ad_id)
        CRUDLink.__calculate_point(db, ad_id=ad_id)

    @staticmethod
    def remove_member_from_link(db: Session, link_id: int, member: str):

        link = db.query(Link).filter_by(id=link_id).first()

        members = link.members or {}
        if not isinstance(members, dict):
            members = {}

        members.pop(str(member), None)

        stmt = (
            update(Link)
            .where(Link.id == link.id)
            .values(
                members=members
            )
        )
        db.execute(stmt)
        db.commit()

        CRUDLink.__set_count(db, link_id=link_id)
        CRUDLink.__calculate_point(db, id=link_id)

    @staticmethod
    def update_has_warning(db: Session, link_id: int, new_value: bool):
        statement = update(Link).where(Link.id == link_id).values(has_warning=new_value)
        db.execute(statement)
        db.commit()

    @staticmethod
    def __set_count(db: Session, ad_id: int = None, link_id: int = None):
        if link_id:
            link = db.query(Link).filter_by(id=link_id).first()
            members = link.members or {}
            if not isinstance(members, dict):
                members = {}

            count = len(members)

            stmt = (
                update(Link)
                .where(Link.id == link.id)
                .values(
                    count=count
                )
            )
            db.execute(stmt)
            db.commit()

        else:
            links = db.query(Link).filter_by(ad_id=ad_id).all()

            if not links:
                return
            for link in links:
                members = link.members or {}
                if not isinstance(members, dict):
                    members = {}
                count = len(members)

                stmt = (
                    update(Link)
                    .where(Link.id == link.id)
                    .values(
                        count=count
                    )
                )
                db.execute(stmt)
                db.commit()

    @staticmethod
    def __calculate_point(db: Session, id: int = None, ad_id: int = None):
        if id:
            statement = select(Link).where(Link.id == id)
            data: Link = db.execute(statement).scalars().first()

            if not data:
                return

            if data.count <= 0:
                statement = update(Link).where(Link.id == id).values(point=0)
            else:
                total_score = 0

                for chat_id, li in data.members.items():
                    total_score += li[1]

                point = total_score / data.count

                statement = update(Link).where(Link.id == id).values(point=point)
        else:
            statement = select(Link).where(Link.ad_id == ad_id)
            data = db.execute(statement).scalars().all()

            if not data:
                return

            for d in data:
                if d.count == 0:
                    statement = update(Link).where(Link.id == d.id).values(point=0)
                else:
                    total_score = 0

                    for chat_id, li in d.members.items():
                        total_score += li[1]

                    point = total_score / d.count

                    statement = update(Link).where(Link.id == d.id).values(point=point)
        db.execute(statement)
        db.commit()
