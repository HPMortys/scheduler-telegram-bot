from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import TlUserModel, ScheduledNotificationModel
from typing import Optional, List
from db.constants import NotificationStatus
from sqlalchemy import or_

engine = create_engine("sqlite:///identifier.sqlite", echo=True)
Session = sessionmaker(bind=engine)
session = Session()


# Dev notes: TODO: !!! redo: change approach !!!
class SqlAlchemyDataBaseApi:
    class BotUsersActions:

        @staticmethod
        def create_user(tl_user_id: int, first_name: str, second_name: Optional[str] = None):
            user = TlUserModel(tl_user_id=tl_user_id, first_name=first_name, second_name=second_name)
            with session:
                session.add(user)
                session.commit()
            return user

        @staticmethod
        def get_user_by_id(user_id: int) -> Optional[TlUserModel]:
            with session:
                return session.query(TlUserModel).get(id=user_id)

        @staticmethod
        def get_user_by_tl_id(tl_user_id: int) -> Optional[TlUserModel]:
            with session:
                return session.query(TlUserModel).get(tl_user_id=tl_user_id)

    # TODO: redo approach
    class ScheduledNotificationsActions:

        @staticmethod
        def create_notification(settings, tl_user_id, user_id=None, status=NotificationStatus.ACTIVE):
            if user_id is None:
                user = SqlAlchemyDataBaseApi.BotUsersActions.get_user_by_tl_id(tl_user_id)
                user_id = user.id
            scheduled_notification = ScheduledNotificationModel(settings=settings, tl_user_id=tl_user_id, status=status)
            scheduled_notification.user = user_id

        @staticmethod
        def get_notification_by_id(notification_id: int) -> Optional[ScheduledNotificationModel]:
            with session:
                return session.query(ScheduledNotificationModel).get(id=notification_id)

        @staticmethod
        def get_notification_by_tl_user_id(tl_user_id: int) -> Optional[List[ScheduledNotificationModel]]:
            notifications = session.query(ScheduledNotificationModel).filter(
                or_(ScheduledNotificationModel.status == NotificationStatus.ACTIVE,
                    ScheduledNotificationModel.status == NotificationStatus.PAUSED),
                tl_user_id=tl_user_id
            ).all()
            return notifications

        @staticmethod
        def archive_notification(notification_id: int):
            notification = SqlAlchemyDataBaseApi.ScheduledNotificationsActions.get_notification_by_id(notification_id)
            if notification:
                with session:
                    notification.status = NotificationStatus.ARCHIVED
                    session.commit()

        @staticmethod
        def delete_notification(notification_id):
            pass
