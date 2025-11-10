from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Boolean, String, Float, DateTime

from database.base import Base


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    main_wallet_address: Mapped[str] = mapped_column(String, nullable=True)
    fee: Mapped[int] = mapped_column(Integer, nullable=True)
    financial_support: Mapped[str] = mapped_column(String, nullable=True)
    advertising_support: Mapped[str] = mapped_column(String, nullable=True)
    is_forced_join_active: Mapped[bool] = mapped_column(Boolean, nullable=True)
    minimum_payout: Mapped[int] = mapped_column(Integer, nullable=True)
    is_auto_transfer: Mapped[bool] = mapped_column(Boolean, nullable=True)
    transfer_wallet_private_key: Mapped[str] = mapped_column(String, nullable=True)
    transfer_wallet_public_key: Mapped[str] = mapped_column(String, nullable=True)
    log_channel_chat_id : Mapped[str] = mapped_column(String, nullable=True)
    main_channel_chat_id: Mapped[str] = mapped_column(String, nullable=True)
    trx_price : Mapped[int] = mapped_column(Integer, nullable=True)
    last_trx_price_update:Mapped[datetime] = mapped_column(DateTime, nullable=True)
