from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, Boolean

from database.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    downloader_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("downloader_users.id", ondelete="CASCADE"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    foreign_account_id: Mapped["Account"] = relationship("Account", foreign_keys=[account_id], passive_deletes=True)
    foreign_downloader_user_id: Mapped["DownloaderUser"] = relationship("DownloaderUser", foreign_keys=[downloader_user_id], passive_deletes=True)
