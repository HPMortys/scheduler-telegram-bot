import enum
from typing import Optional, Any, List
from datetime import datetime
from sqlalchemy import create_engine, Table, Column, MetaData, INTEGER, String, JSON, func, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map = {
        dict[str, Any]: JSON
    }


class TlUser(Base):
    __tablename__ = "notifier_bot_users_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    tl_user_id: Mapped[int] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column(String(32))
    second_name: Mapped[Optional[str]] = mapped_column(String(32))
    date_create: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    scheduled_notifications: Mapped[List["ScheduledNotification"]] = relationship()


class NotificationStatus(enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ScheduledNotification(Base):
    __tablename__ = "scheduled_notifications_table"

    id: Mapped[int] = mapped_column(primary_key=True)
    settings: Mapped[dict[str, Any]]
    tl_user_id: Mapped[int]
    user_id: Mapped[int] = mapped_column(ForeignKey('notifier_bot_users_table.id'))
    user: Mapped["TlUser"] = relationship(back_populates="scheduled_notifications")
    status: Mapped[NotificationStatus]
    date_create: Mapped[datetime] = mapped_column(DateTime(timezone=True), insert_default=func.now)
