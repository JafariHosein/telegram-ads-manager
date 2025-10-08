import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, Boolean, Enum, String, BIGINT

from database.base import Base


class PayoutRequestType(enum.Enum):
    RIAL = "rial"
    TRON = "tron"


class PayoutRequestDestinationType(enum.Enum):
    CARD = "card"
    SHABA = "shaba"
    TRON = "tron"


class PayoutRequestStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    REJECTED = "rejected"


class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[PayoutRequestType] = mapped_column(Enum(PayoutRequestType), nullable=False)
    destination_type: Mapped[PayoutRequestDestinationType] = mapped_column(Enum(PayoutRequestDestinationType), nullable=False)
    wallet_address: Mapped[str] = mapped_column(String, nullable=True)
    bank_id: Mapped[int] = mapped_column(Integer, ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=True)
    amount: Mapped[int] = mapped_column(BIGINT, nullable=False)
    status: Mapped[PayoutRequestStatus] = mapped_column(Enum(PayoutRequestStatus), nullable=False, default=PayoutRequestStatus.PENDING)
    reason: Mapped[str] = mapped_column(String, nullable=True)
    auto_complete: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)

    foreign_account_id: Mapped["Account"] = relationship("Account", foreign_keys=[account_id], passive_deletes=True)
    foreign_bank_id: Mapped["BankAccount"] = relationship("BankAccount", foreign_keys=[bank_id], passive_deletes=True)
