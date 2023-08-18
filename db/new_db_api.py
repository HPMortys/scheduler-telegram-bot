from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import TlUser, ScheduledNotification

engine = create_engine("sqlite:///test.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()


class SqlAlchemyDataBaseApi:
    class BotUsers:

        def save_user(self, ):
            with session as s:
                a = TlUser()

                s.add()
