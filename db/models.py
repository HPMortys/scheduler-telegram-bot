from typing import Optional, Any, List
from datetime import datetime
from sqlalchemy import String, JSON, func, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from db.constants import NotificationStatus


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSON
    }


class TlUserModel(Base):
    __tablename__ = "users_notifier_bot_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    tl_user_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(String(32))
    second_name: Mapped[Optional[str]] = mapped_column(String(32))
    date_create: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    scheduled_notifications: Mapped[List["ScheduledNotificationModel"]] = relationship(cascade="all, delete")


class ScheduledNotificationModel(Base):
    __tablename__ = "scheduled_notifications_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    settings: Mapped[dict[str, Any]]
    tl_user_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey('users_notifier_bot_table.id'))
    user: Mapped["TlUserModel"] = relationship(back_populates="scheduled_notifications")
    status: Mapped[NotificationStatus] = mapped_column(default=NotificationStatus.ACTIVE)
    date_create: Mapped[datetime] = mapped_column(DateTime(timezone=True), insert_default=func.now)
