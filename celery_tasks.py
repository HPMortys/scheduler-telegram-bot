from celery import Celery
from datetime import datetime
import json

from db.db_api import Database

from telegram_bot.bot import send_message_to_user

app = Celery('hello', broker='amqp://guest@localhost/')
app.config_from_object('celeryconfig')


def get_schedules():
    db = Database()
    schedules = db.select_rows(table_name=Database.Tables.scheduler_test)
    return schedules


@app.task(ignore_result=True)
def scheduler_task():
    now = datetime.now().time().strftime("%H:%M")
    schedules = get_schedules()

    for schedule in schedules:
        tl_user_id = schedule[1]
        schedule_data = json.loads(schedule[2])
        if schedule_data['time'] == now:
            send_message_to_user(tl_user_id=tl_user_id, message=schedule_data['content'])
