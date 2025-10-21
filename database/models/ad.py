import enum
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, Boolean, String, Enum

from database.base import Base


class AdChannelType(enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"


class AdChannelTypeFarsi(enum.Enum):
    PRIVATE = "🔒 خصوصی"
    PUBLIC = "🌐 عمومی"


class AdLinkType(enum.Enum):
    NORMAL = "normal"
    REQUEST = "request"
    BOTH = "both"

class AdLinkTypeFarsi(enum.Enum):
    NORMAL = "🟢 عادی"
    REQUEST = "📩 درخواستی"
    BOTH = "🎯 انتخاب توسط دانلودر"


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer_users.id"), nullable=True)
    channel_chat_id: Mapped[str] = mapped_column(String, nullable=False)
    channel_name: Mapped[str] = mapped_column(String, nullable=False)
    channel_type: Mapped[AdChannelType] = mapped_column(Enum(AdChannelType), nullable=False)
    channel_username: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rate: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    auto_complete: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    link_type: Mapped[AdLinkType] = mapped_column(Enum(AdLinkType), nullable=False, default=AdLinkType.NORMAL)
    category_title: Mapped[str] = mapped_column(String, nullable=False)
    prize: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)

    foreign_customer_user_id: Mapped["CustomerUser"] = relationship("CustomerUser", foreign_keys=[customer_user_id], passive_deletes=True)
