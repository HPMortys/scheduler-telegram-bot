from datetime import datetime
from telegram_bot.bot import send_message
import json

weeks_schedule = {
    0: [{'subject': 'Machine Learning1', 'data': ''}, {'subject': 'Innovative development', 'data': ''}],
    1: [{'subject': 'Machine Learning2', 'data': ''}, {'subject': 'Innovative development', 'data': ''}],
    2: [{'subject': 'Machine Learning3', 'data': ''}, {'subject': 'Innovative development', 'data': ''}],
    3: [{'subject': 'Machine Learning4', 'data': ''}, {'subject': 'Innovative development', 'data': ''}],
    4: [{'subject': 'Machine Learning5', 'data': ''}, {'subject': 'Innovative development', 'data': ''}],
    5: [{'subject': 'Machine Learning6', 'data': ''}, {'subject': 'Innovative development', 'data': ''}],
    6: [{'subject': 'Machine Learning7', 'data': ''}, {'subject': 'Innovative development', 'data': ''}]
}


def schedule():
    week_day = datetime.now().weekday()
    schedule_data = json.dumps(weeks_schedule[week_day])
    send_message(schedule_data)

    data = {'success': True}
    return data
