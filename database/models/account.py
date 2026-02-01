import enum
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, String, BIGINT, ARRAY, Enum, ForeignKey

from database.base import Base


class AccountRole(enum.Enum):
    ADMIN = "admin"
    DOWNLOADER = "downloader"

class AccountRoleFarsi(enum.Enum):
    ADMIN = "👑 ادمین"
    DOWNLOADER = "📥 دانلودر"

class AccountStatus(enum.Enum):
    BANNED = "banned"
    ACTIVE = "active"

class AccountStatusFarsi(enum.Enum):
    BANNED = "🚫 بن"
    ACTIVE = "✅ فعال"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    balance: Mapped[int] = mapped_column(BIGINT, nullable=False, default=0)
    ad_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False, default=[])
    linked_username: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    role: Mapped[AccountRole] = mapped_column(Enum(AccountRole), nullable=False, default=AccountRole.DOWNLOADER)
    username: Mapped[str] = mapped_column(String, ForeignKey("downloader_users.chat_id", ondelete="CASCADE"), nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    foreign_username: Mapped["DownloaderUser"] = relationship("DownloaderUser", foreign_keys=[username], passive_deletes=True)


