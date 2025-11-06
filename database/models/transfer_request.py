import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, Boolean, BIGINT, Enum, String

from database.base import Base


class TransferRequestStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"

class TransferRequestStatusFarsi(enum.Enum):
    PENDING = "🕓 در انتظار تأیید"
    COMPLETED = "✅ تأیید شده"
    REJECTED = "❌ رد شده"


class TransferRequest(Base):
    __tablename__ = "transfer_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    target_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    amount: Mapped[int] = mapped_column(BIGINT, nullable=False, default=0)
    status: Mapped[TransferRequestStatus] = mapped_column(Enum(TransferRequestStatus), nullable=False, default=TransferRequestStatus.PENDING)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    auto_completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    foreign_account_id: Mapped["Account"] = relationship("Account", foreign_keys=[account_id], passive_deletes=True)
    foreign_target_account_id: Mapped["Account"] = relationship("Account", foreign_keys=[target_account_id], passive_deletes=True)
