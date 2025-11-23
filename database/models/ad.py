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


class AdLinkTypeFarsi(enum.Enum):
    NORMAL = "🟢 عادی"
    REQUEST = "📩 درخواستی"


class AdStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNVERIFIED = "unverified"
    COMPLETED = "completed"


class AdStatusFarsi(enum.Enum):
    ACTIVE = "🟢 فعال"
    INACTIVE = "⛔ غیر فعال"
    UNVERIFIED = "⚠️ حسابرسی نشده"
    COMPLETED = "✅ حسابرسی شده"


class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer_users.id"), nullable=True)
    channel_chat_id: Mapped[str] = mapped_column(String, nullable=False)
    channel_name: Mapped[str] = mapped_column(String, nullable=False)
    channel_type: Mapped[AdChannelType] = mapped_column(Enum(AdChannelType), nullable=False)
    channel_username: Mapped[str] = mapped_column(String, nullable=True)
    channel_link: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rate: Mapped[int] = mapped_column(Integer, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    auto_complete: Mapped[bool] = mapped_column(Boolean, nullable=False)
    status: Mapped[AdStatus] = mapped_column(Enum(AdStatus), nullable=False, default=AdStatus.ACTIVE)
    link_type: Mapped[AdLinkType] = mapped_column(Enum(AdLinkType), nullable=False, default=AdLinkType.NORMAL)
    prize: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)

    foreign_customer_user_id: Mapped["CustomerUser"] = relationship("CustomerUser", foreign_keys=[customer_user_id], passive_deletes=True)
