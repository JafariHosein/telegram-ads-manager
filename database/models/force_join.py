from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String

from database.base import Base


class ForceJoin(Base):
    __tablename__ = "force_joins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
