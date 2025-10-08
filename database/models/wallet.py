import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, String, Enum, Float

from database.base import Base


class WalletStatus(enum.Enum):
    UNUSED = "unused"
    RECEIVED = "received"
    COMPLETED = "completed"


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer_users.id", ondelete="CASCADE"), nullable=False)
    private_key: Mapped[str] = mapped_column(String, nullable=False)
    public_key: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[WalletStatus] = mapped_column(Enum(WalletStatus), nullable=False, default=WalletStatus.UNUSED)
    received_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)

    foreign_customer_user_id: Mapped["CustomerUser"] = relationship("CustomerUser", foreign_keys=[customer_user_id], passive_deletes=True)
