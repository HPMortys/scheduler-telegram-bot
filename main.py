from logger.logger_config import logger

from telegram_bot.bot import bot
from utils_general.exceptions import UnknownBotException


# TODO: temp


# logging.basicConfig(filemode='w', filename='app.log')

# handler = logging.StreamHandler()
# formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
# handler.setFormatter(formatter)
# logger.addHandler(handler)

if __name__ == '__main__':
    logger.info('Start')
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except UnknownBotException as e:
            logger.error(f'An exception occured in the polling loop: {e}')
            break
