import enum
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, Enum, String

from database.base import Base


class RegisterRequestStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class RegisterRequestStatusFarsi(enum.Enum):
    PENDING = "🕓 در انتظار تأیید"
    APPROVED = "✅ تأیید شده"
    REJECTED = "❌ رد شده"

class RegisterRequest(Base):
    __tablename__ = "register_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    linked_username: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[RegisterRequestStatus] = mapped_column(Enum(RegisterRequestStatus), nullable=False, default=RegisterRequestStatus.PENDING)
    downloader_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("downloader_users.id", ondelete="CASCADE"), nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    foreign_downloader_user: Mapped["DownloaderUser"] = relationship("DownloaderUser", foreign_keys=[downloader_user_id], passive_deletes=True)
