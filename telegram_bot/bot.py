import logging
import json

import telebot
from telebot import types

from telegram_bot.constants import BOT_TOKEN
from db.db_api import Database
from telegram_bot.utils.validation_utils import is_time_format_valid, is_content_input_step_valid

bot = telebot.TeleBot(BOT_TOKEN)

# TODO: delete
temp_user = 418980357

# ❌

messages_templates = \
    {
        '/start':
            '''
            --- BOT IS UNDER MAINTENANCE ---
            Hey {user}, welcome to scheduler bot.
            
            Bot allows to create scheduled notifications. 
            Use following commands to interact with bot.
             
            /getSchedule - to show your notification
            /addSchedule - to add new scheduled notification 
            /deleteScheduler - to delete specific scheduler
            ''',
        '/help':
            '''
        
            ''',
        '/getSchedule':
            '''
             Your schedule:\n{schedule}
            ''',
        '/addSchedule':
            {
                0:
                    '''
                    Input data that will be sent by schedule  
                    ''',
                1:
                    '''
                    Set date in 24-hour format, for instance 15:00, 01:30, 00:00, etc 
                    ''',
                2:
                    '''
                    Choose notification week days
                    ''',
                3:
                    '''
                    Your schedule successfully updated 👍
                    '''
            },
        '/updateScheduler':
            '''
            ''',
        '/deleteScheduler':
            '''
            Input the following id of schedule that you want to delete:\n{schedule} 
            '''
    }

undefined_template = '''
Sorry but I do not understand, use /help
'''


class ButtonsText:
    ADD_SCHEDULED_NOTIFICATION: str = '➕ New scheduled notification ➕'
    GET_SCHEDULED_NOTIFICATIONS: str = '📃 Your scheduled notifications 📃'
    CANCEL_BUTTON_TEXT: str = '❌ Cancel'


logger = logging.getLogger(__name__)
logging.basicConfig(filemode='w', filename='app.log')

handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class ScheduleMessages:
    def __init__(self, chat_id: int, user_id: int, content: str = None, time: str = None, days: list = None):
        self.chat_id: int = chat_id
        self.user_id: int = user_id
        self.content: str = content
        self.time: str = time
        self.days: list = days


user_schedule_dict: dict[str, ScheduleMessages] = {}


def send_message(message=None):
    if message:
        bot.send_message(418980357, message)


def get_menu_keyboard_markup() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(ButtonsText.ADD_SCHEDULED_NOTIFICATION)
    item2 = types.KeyboardButton(ButtonsText.GET_SCHEDULED_NOTIFICATIONS)
    markup.add(item1, item2)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    message_text: str = messages_templates.get('/start', 'undefined')
    message_data: dict = {'user': message.from_user.username}
    bot.send_message(message.from_user.id, message_text.format(**message_data), reply_markup=get_menu_keyboard_markup())


@bot.message_handler(commands=['getSchedule'])
def getSchedule(message):
    message_text: str = messages_templates.get('/getSchedule', 'undefined')
    message_data: dict = {}

    schedule_data = get_schedules(message.from_user.id)

    processed_data = ''
    for idx, data in enumerate(schedule_data):
        schedule_data = json.loads(data[2])
        week_days_data: list = schedule_data.get("week_days", ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
        processed_data += f"\n ***#{idx} - *** {schedule_data['content']}\n" \
                          f"> {schedule_data['time']}\n" \
                          f" {', '.join(week_days_data)}\n" + '-' * 10 + '\n'

    message_data['schedule'] = processed_data
    bot.send_message(message.from_user.id, message_text.format(**message_data), parse_mode="Markdown")


def get_schedules(tl_user_id):
    db = Database()
    schedules = db.select_rows(table_name=Database.Tables.scheduler_test, where={'tl_user_id': tl_user_id})
    return schedules


@bot.message_handler(commands=['addSchedule'])
def addSchedule(message):
    message_text = messages_templates.get('/addSchedule', 'undefined')
    message_data: dict = {}
    message_text = message_text[0]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(ButtonsText.CANCEL_BUTTON_TEXT)
    markup.add(item1)

    bot.register_next_step_handler(message, process_time_step)
    bot.send_message(message.from_user.id, message_text.format(**message_data), reply_markup=markup)


def cancel_operation_wrapper(func):
    def wrapper(*args, **kwargs):
        for msg in args:
            if isinstance(msg, types.Message) and msg.text == ButtonsText.CANCEL_BUTTON_TEXT:
                bot.send_message(msg.from_user.id, '❌ Operation canceled ❌', reply_markup=get_menu_keyboard_markup())
                return
        return func(*args, **kwargs)

    return wrapper


@cancel_operation_wrapper
def process_time_step(message):
    # markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True)
    # markup.add('Male', 'Female')

    chat_id = message.chat.id
    user_id = message.from_user.id
    key: str = str(chat_id) + str(user_id)
    schedule_message = ScheduleMessages(chat_id, user_id)

    # TODO: possible data validation
    content = message.text

    # stored results of content input step
    schedule_message.content = content
    user_schedule_dict[key] = schedule_message

    # next step
    msg = bot.reply_to(message, messages_templates['/addSchedule'][1])
    bot.register_next_step_handler(msg, process_week_days_step)


@cancel_operation_wrapper
def process_week_days_step(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    key: str = str(chat_id) + str(user_id)

    # validation
    time = message.text
    if not is_time_format_valid(time):
        msg = bot.reply_to(
            message,
            'Time is *NOT* responded to general time format - "H:M", like 13:40, 01:20, etc. *Try again*',
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, process_week_days_step)
        return

    # stored results of time input step
    schedule_message = user_schedule_dict[key]
    schedule_message.time = time
    markup = get_week_days_keyboard_markup()

    msg = bot.send_message(message.from_user.id,
                           text=messages_templates['/addSchedule'][2],
                           reply_markup=markup)


def get_week_days_keyboard_markup(options: dict[int, str] = None):
    markup = types.InlineKeyboardMarkup()
    selected_days = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
    if options is not None:
        selected_days.update(options)
    for key, day in selected_days.items():
        markup.add(types.InlineKeyboardButton(
            text=day,
            callback_data=f"selected_day_data:{key}, {day}")
        )
    markup.add(types.InlineKeyboardButton(text='DONE ✅', callback_data="selected_day_data:DONE"))
    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith("selected_day_data:"))
def week_days_button_click(call):
    markup = call.message.reply_markup
    old_keyboard = markup.keyboard
    # TODO: rethink saving approach
    if 'DONE' in call.data:
        chat_id = call.message.chat.id
        user_id = call.from_user.id
        key: str = str(chat_id) + str(user_id)

        # validation
        days = []
        for idx, button_data in enumerate(old_keyboard):
            button = button_data[0]
            if button.text.startswith('🌟'):
                days.append(idx)
        # storing results of days choosing step
        schedule_message = user_schedule_dict[key]
        schedule_message.days = days

        # TODO: rethink saving approach
        process_data_save_step(call)
        user_schedule_dict.pop(key)
    else:
        selected_day_data: list[str] = call.data.replace('selected_day_data:', '').split(', ')
        selected_day: str = str(selected_day_data[1])
        new_keyboard = markup.keyboard
        for idx, button_data in enumerate(old_keyboard):
            old_button = button_data[0]
            if selected_day in old_button.text:
                if old_button.text.startswith('🌟'):
                    old_button.text = f'{selected_day}'
                else:
                    old_button.text = f'🌟 {selected_day}'
                new_keyboard[idx][0] = old_button
        markup.keyboard = new_keyboard

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=call.message.text,
            reply_markup=markup)


def process_data_save_step(call):
    # TODO: Redo
    # chat_id = message.chat.id
    # user_id = message.from_user.id
    # key: str = str(chat_id) + str(user_id)
    # # TODO: think how to change logic approach
    # schedule_message = user_schedule_dict[key]
    # print(schedule_message).
    # save_schedule_data(schedule_message)
    bot.reply_to(call.message, messages_templates['/addSchedule'][3], parse_mode="Markdown")


def save_schedule_data(content):
    # TODO: Redo

    user_data = content['user_data']
    schedule_data = content['schedule_data']

    db = Database()

    user = db.select_rows(table_name=Database.Tables.user, where={'tl_user_id': user_data['tl_user_id']})
    if not user:
        db.insert_row(Database.Tables.user, user_data)

    db.insert_row(Database.Tables.scheduler_test, schedule_data)


@bot.message_handler(commands=['delEvent'])
def delete_event_reminder(message):
    pass


# @bot.message_handler(func=lambda message: 'Cancel' in message.text)
@bot.message_handler(content_types=['text'])
def menu_button_func(message):
    if message.text == ButtonsText.ADD_SCHEDULED_NOTIFICATION:
        addSchedule(message)
    elif message.text == ButtonsText.GET_SCHEDULED_NOTIFICATIONS:
        getSchedule(message)
    elif message.text == ButtonsText.CANCEL_BUTTON_TEXT:
        start(message)


if __name__ == '__main__':
    logger.info('Start')
    bot.polling(none_stop=True, interval=0)
