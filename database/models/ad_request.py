import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, String, Enum, BIGINT

from database.base import Base


class AdRequestChannelType(enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class AdRequestStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"


class AdRequest(Base):
    __tablename__ = "ad_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer_users.id", ondelete="CASCADE"), nullable=False)
    channel_chat_id: Mapped[str] = mapped_column(String, nullable=False)
    channel_name: Mapped[str] = mapped_column(String, nullable=False)
    channel_type: Mapped[AdRequestChannelType] = mapped_column(Enum(AdRequestChannelType), nullable=False)
    channel_username: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    rate: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_without_fee: Mapped[int] = mapped_column(BIGINT, nullable=False)
    final_price: Mapped[int] = mapped_column(BIGINT, nullable=False)
    status: Mapped[AdRequestStatus] = mapped_column(Enum(AdRequestStatus), nullable=False, default=AdRequestStatus.PENDING)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)

    foreign_customer_user_id: Mapped["CustomerUser"] = relationship("CustomerUser", foreign_keys=[customer_user_id], passive_deletes=True)
