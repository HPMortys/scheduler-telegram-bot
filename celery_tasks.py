import json
import os
from concurrent.futures import ThreadPoolExecutor
from celery import Celery
from datetime import datetime

from constants import BROKER
from db.new_db_api import SqlAlchemyDataBaseApi
from db.models import ScheduledNotificationModel

from telegram_bot.bot import bot

app = Celery('hello', broker='amqp://guest@localhost/')
app.config_from_object('celeryconfig')
app.autodiscover_tasks()

max_workers: int = os.cpu_count() * 2


@app.task(ignore_result=True, expires=900)
def scheduler_task():
    db = SqlAlchemyDataBaseApi()
    active_notifications = db.get_all_notifications()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(send_notification_check, active_notifications)
    return active_notifications


def send_notification_check(notification: ScheduledNotificationModel):
    now = datetime.now(tz=None)
    current_time = now.time().strftime("%H:%M")
    current_day = now.weekday()
    tl_user_id = notification.tl_user_id
    schedule_data = json.loads(notification.settings)
    print(schedule_data)
    print(schedule_data['time'] == current_time and current_day in schedule_data['week_days'])
    if schedule_data['time'] == current_time and current_day in schedule_data['week_days']:
        print('YES')
        bot.send_message(int(tl_user_id), schedule_data['content'])
app.send_task('celery_tasks.scheduler_task')
