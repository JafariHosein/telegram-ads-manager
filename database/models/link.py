
from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, Integer, ForeignKey, Boolean, String, Float

from database.base import Base

class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    ad_id: Mapped[int] = mapped_column(Integer, ForeignKey("ads.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    is_request_type: Mapped[bool] = mapped_column(Boolean, nullable=False)
    members: Mapped[dict] = mapped_column(JSONB, nullable=False, default={})
    point: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    has_warning: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)

    foreign_account_id: Mapped["Account"] = relationship("Account", foreign_keys=[account_id], passive_deletes=True)
