import logging
import json

import telebot
from telebot import types

from telegram_bot.constants import BOT_TOKEN
from db.db_api import Database
from db.new_db_api import SqlAlchemyDataBaseApi
from db.constants import NotificationStatus
from db.models import ScheduledNotificationModel
from telegram_bot.utils.validation_utils import is_time_format_valid, is_content_input_step_valid
from utils_general.utils import week_data_data_transform

bot = telebot.TeleBot(BOT_TOKEN)

# TODO: delete

# ❌

messages_templates = \
    {
        '/start':
        '''
--- BOT IS UNDER MAINTENANCE ---
Hey {user}, welcome to scheduler bot.

Bot allows to create scheduled notifications. 
Use following commands to interact with bot.
 
/addSchedule - to add new scheduled notification 
/statusSchedule - to update, delete, pause or activate your scheduled notifications
/getSchedule - to show your notification (temporary)
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
        '/statusSchedule':
            ''' 
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


class ScheduledNotification:
    def __init__(self, chat_id: int, tl_user_id: int, content: str = None, time: str = None, days: list = None):
        self.chat_id: int = chat_id
        self.tl_user_id: int = tl_user_id
        self.content: str = content
        self.time: str = time
        self.days: list = days


user_schedule_dict: dict[str, ScheduledNotification] = {}
user_notification_data: dict[str, list] = {}


def get_menu_keyboard_markup() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(ButtonsText.ADD_SCHEDULED_NOTIFICATION)
    item2 = types.KeyboardButton(ButtonsText.GET_SCHEDULED_NOTIFICATIONS)
    markup.add(item1, item2)
    return markup


# TODO: save user
@bot.message_handler(commands=['start', 'help', 'info'])
def start(message):
    message_text: str = messages_templates.get('/start', 'undefined')
    message_data: dict = {'user': message.from_user.username}
    # TODO: save user
    bot.send_message(message.from_user.id, message_text.format(**message_data), reply_markup=get_menu_keyboard_markup())


# TODO: mb delete
@bot.message_handler(commands=['getSchedule'])
def getSchedule(message):
    message_text: str = messages_templates.get('/getSchedule', 'undefined')
    message_data: dict = {}

    tl_user_id = message.from_user.id

    db_api = SqlAlchemyDataBaseApi()
    user_scheduled_data = db_api.get_notification_by_tl_user_id(tl_user_id)

    processed_data = ''
    for idx, notification_data in enumerate(user_scheduled_data):
        settings_data: dict = json.loads(notification_data.settings)
        week_days_data: list = week_data_data_transform(settings_data.get('week_days', ''))
        processed_data += f"\n ***[#{idx}] - status: {notification_data.status}*** \n{settings_data.get('content', '')}\n\n" \
                          f"> {settings_data.get('time', '')}\n" \
                          f" {', '.join(week_days_data)}\n" + '=' * 10 + '\n\n'

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
    chat_id = message.chat.id
    tl_user_id = message.from_user.id
    key: str = str(chat_id) + str(tl_user_id)
    schedule_message = ScheduledNotification(chat_id=chat_id, tl_user_id=tl_user_id)

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
    tl_user_id = message.from_user.id
    key: str = str(chat_id) + str(tl_user_id)

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
def week_days_button_click_callback(call):
    markup = call.message.reply_markup
    old_keyboard = markup.keyboard
    # TODO: rethink saving approach
    if 'DONE' in call.data:
        chat_id = call.message.chat.id
        tl_user_id = call.from_user.id
        key: str = str(chat_id) + str(tl_user_id)

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
    chat_id = call.message.chat.id
    tl_user_id = call.from_user.id
    key: str = str(chat_id) + str(tl_user_id)

    notification_data: ScheduledNotification = user_schedule_dict[key]

    db_api = SqlAlchemyDataBaseApi()

    user = db_api.get_user_by_tl_id(tl_user_id=notification_data.tl_user_id)
    if not user:
        user = db_api.create_user(
            tl_user_id=tl_user_id,
            first_name=call.from_user.first_name,
            last_name=call.from_user.last_name,
            username=call.from_user.username
        )

    settings = json.dumps(
        {'content': notification_data.content, 'week_days': notification_data.days, 'time': notification_data.time})
    db_api.create_notification(settings=settings, tl_user_id=tl_user_id, user_id=user.id)
    del db_api

    bot.send_message(call.from_user.id, messages_templates['/addSchedule'][3],
                     parse_mode="Markdown", reply_markup=get_menu_keyboard_markup())


def save_scheduled_data(content):
    # TODO: Redo

    user_data = content['user_data']
    schedule_data = content['schedule_data']

    db = Database()

    user = db.select_rows(table_name=Database.Tables.user, where={'tl_user_id': user_data['tl_user_id']})
    if not user:
        db.insert_row(Database.Tables.user, user_data)

    db.insert_row(Database.Tables.scheduler_test, schedule_data)


def get_notification_status_change_markup(notification_id: int, current_notification_idx: int):
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('🗑 Delete',
                                       callback_data=f'change_status:{NotificationStatus.ARCHIVED.value},{notification_id}')
    item2 = types.InlineKeyboardButton('⛔ Suspend',
                                       callback_data=f'change_status:{NotificationStatus.PAUSED.value},{notification_id}')
    item3 = types.InlineKeyboardButton('🟢 Activate',
                                       callback_data=f'change_status:{NotificationStatus.ACTIVE.value},{notification_id}')
    item4 = types.InlineKeyboardButton('Previous',
                                       callback_data=f'notification_selection:PREVIOUS,{current_notification_idx}')

    item5 = types.InlineKeyboardButton('Next',
                                       callback_data=f'notification_selection:NEXT,{current_notification_idx}')

    markup.add(item1, item2, item3, item4, item5)
    return markup


def get_str_notification_data(notification_obj: ScheduledNotificationModel, idx: int = 0):
    settings_data: dict = json.loads(notification_obj.settings)
    week_days_data: list = week_data_data_transform(settings_data.get('week_days', ''))
    content = f"\n ***[#{idx}] - status: {notification_obj.status.value}*** \n{settings_data.get('content', '')}\n\n" \
              f"> {settings_data.get('time', '')}\n " \
              f"{', '.join(week_days_data)}\n" + '=' * 10 + '\n\n'
    return content


# TODO: redo - repeated code parts
@bot.message_handler(commands=['statusSchedule'])
def statusSchedule(message):
    # message_text: str = messages_templates.get('/deleteSchedule', 'undefined')
    # message_data: dict = {}

    chat_id = message.chat.id
    tl_user_id = message.from_user.id
    key: str = str(chat_id) + str(tl_user_id)

    db_api = SqlAlchemyDataBaseApi()
    user_scheduled_data = db_api.get_notification_by_tl_user_id(tl_user_id)

    processed_data_sap: list[dict] = []
    for idx, notification_data in enumerate(user_scheduled_data):
        content = get_str_notification_data(notification_obj=notification_data, idx=idx)
        processed_data_sap_dict = {'notification_id': notification_data.id, 'content': content}
        processed_data_sap.append(processed_data_sap_dict)

    user_notification_data[key] = processed_data_sap

    if processed_data_sap:
        bot.send_message(message.from_user.id, processed_data_sap[0]['content'],
                         parse_mode="Markdown", reply_markup=get_notification_status_change_markup(
                processed_data_sap[0]['notification_id'], 0))
    else:
        bot.send_message(message.from_user.id, 'You do not have scheduled notifications', parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith("notification_selection:"))
def notification_choosing_button_callback(call):
    selected_notification_selection_data: list[str] = call.data.replace('notification_selection:', '').split(',')
    # TODO: redo
    selection_action: str = str(selected_notification_selection_data[0])
    selection_current_notification_idx: int = int(selected_notification_selection_data[1])

    chat_id = call.message.chat.id
    tl_user_id = call.from_user.id
    key: str = str(chat_id) + str(tl_user_id)
    user_scheduled_data = user_notification_data[key]

    new_notification_idx = 0
    if selection_action == 'PREVIOUS':
        new_notification_idx = (selection_current_notification_idx - 1) % len(user_scheduled_data)
    elif selection_action == 'NEXT':
        new_notification_idx = (selection_current_notification_idx + 1) % len(user_scheduled_data)

    next_notification_data = user_scheduled_data[new_notification_idx]

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=next_notification_data['content'],
        reply_markup=get_notification_status_change_markup(next_notification_data['notification_id'], new_notification_idx),
        parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith("change_status:"))
def change_notification_status_button_callback(call):
    selected_status_data: list[str] = call.data.replace('change_status:', '').split(',')
    selected_status: str = selected_status_data[0]
    selected_notification_id: int = int(selected_status_data[1])
    db_api = SqlAlchemyDataBaseApi()
    db_api.change_notification_status(selected_notification_id, selected_status)

    match selected_status:
        case NotificationStatus.ACTIVE.value:
            bot.answer_callback_query(call.id, 'Was Activated', show_alert=True)
        case NotificationStatus.PAUSED.value:
            bot.answer_callback_query(call.id, 'Was Paused', show_alert=True)
        case NotificationStatus.ARCHIVED.value:
            bot.answer_callback_query(call.id, 'Was Deleted', show_alert=True)


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
