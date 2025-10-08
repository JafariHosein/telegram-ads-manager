from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, BIGINT

from database.base import Base


class AdCategory(Base):
    __tablename__ = "ad_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    min_rate: Mapped[int] = mapped_column(BIGINT, nullable=False)
