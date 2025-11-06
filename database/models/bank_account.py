import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, Enum, String

from database.base import Base


class BankAccountType(enum.Enum):
    SHABA = "shaba"
    CARD = "card"

class BankAccountTypeFarsi(enum.Enum):
    SHABA = "شبا"
    CARD = "شماره کارت"


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[BankAccountType] = mapped_column(Enum(BankAccountType), nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    foreign_account_id: Mapped["Account"] = relationship("Account", foreign_keys=[account_id], passive_deletes=True)
