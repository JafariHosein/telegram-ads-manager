import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, BIGINT, Enum

from database.base import Base


class CustomerUserRole(enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"


class CustomerUser(Base):
    __tablename__ = "customer_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    state: Mapped[str] = mapped_column(String, nullable=True)
    state_data: Mapped[str] = mapped_column(String, nullable=True)
    balance: Mapped[int] = mapped_column(BIGINT, nullable=False, default=0)
    bot_last_message_id: Mapped[int] = mapped_column(Integer, nullable=True)
    role: Mapped[CustomerUserRole] = mapped_column(Enum(CustomerUserRole), nullable=False, default=CustomerUserRole.CUSTOMER)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
