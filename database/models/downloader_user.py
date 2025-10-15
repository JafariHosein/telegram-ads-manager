import enum
from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, Integer, String, Boolean

from database.base import Base


class DownloaderUser(Base):
    __tablename__ = "downloader_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=True)
    state_data: Mapped[str] = mapped_column(String, nullable=True)
    bot_last_message_id: Mapped[int] = mapped_column(Integer, nullable=True)
    can_use_bot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    captcha_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
