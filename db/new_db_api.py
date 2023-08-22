from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import TlUserModel, ScheduledNotificationModel
from typing import Optional, List, Literal
from db.constants import NotificationStatus
from sqlalchemy import or_


# Dev notes: TODO: !!! redo: change approach !!!
class SqlAlchemyDataBaseApi:

    def __init__(self):
        engine = create_engine("sqlite:///D:\\IT_projects\\Scheduler\\identifier.sqlite", echo=True)
        session_obj = sessionmaker(bind=engine)
        self.session = session_obj()
        # self.bot_users_actions = self.BotUsersActions(self)
        # self.scheduled_notifications_actions = self.ScheduledNotificationsActions(self)

    def create_user(self, tl_user_id: int, first_name: str, username: str, last_name: Optional[str] = None):
        user = TlUserModel(tl_user_id=tl_user_id, first_name=first_name, username=username, last_name=last_name)
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_id(self, user_id: int) -> Optional[TlUserModel]:
        return self.session.query(TlUserModel).get(user_id)

    def get_user_by_tl_id(self, tl_user_id: int) -> Optional[TlUserModel]:
        return self.session.query(TlUserModel).filter(TlUserModel.tl_user_id == tl_user_id).first()

    ###

    def create_notification(self, settings, tl_user_id, user_id=None, status=NotificationStatus.ACTIVE.value):
        scheduled_notification = ScheduledNotificationModel(
            settings=settings, tl_user_id=tl_user_id,
            status=status, user_id=user_id
        )
        if user_id is None:
            user = self.get_user_by_tl_id(tl_user_id)
            scheduled_notification.user_id = user.id
        self.session.add(scheduled_notification)
        self.session.commit()

    def get_notification_by_id(self, notification_id: int) -> Optional[ScheduledNotificationModel]:
        return self.session.query(ScheduledNotificationModel).get(notification_id)

    def get_notification_by_tl_user_id(self, tl_user_id: int) -> Optional[List[ScheduledNotificationModel]]:
        notifications = self.session.query(ScheduledNotificationModel).filter(
            or_(ScheduledNotificationModel.status == NotificationStatus.ACTIVE,
                ScheduledNotificationModel.status == NotificationStatus.PAUSED),
            ScheduledNotificationModel.tl_user_id == tl_user_id
        ).all()
        return notifications

    def archive_notification(self, notification_id: int):
        self.change_notification_status(notification_id, NotificationStatus.ARCHIVED.value)

    def change_notification_status(self, notification_id: int, status: NotificationStatus | str):
        notification = self.get_notification_by_id(notification_id)
        if notification:
            notification.status = status
            self.session.commit()

    def delete_notification(self, notification_id: int):
        notification = self.get_notification_by_id(notification_id)
        if notification:
            self.session.delete(notification)
            self.session.commit()

    def __del__(self):
        self.session.close()
