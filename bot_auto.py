import logging
import traceback

from time import sleep

import telegram
import argparse
from environs import Env

import requests


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot: telegram.Bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    env = Env()
    env.read_env()
    headers = {'Authorization': f'Token {env.str("DVMN_TOKEN")}'}
    chat_id = env.str('CHAT_ID')
    params = {}
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('MyLogger')
    logger.setLevel(logging.INFO)
    bot = telegram.Bot(token=env.str('TG_CLIENTS_TOKEN'))
    logger.addHandler(TelegramLogsHandler(bot, chat_id))
    logger.info('Bot started successfully')
    while True:
        try:
            response = requests.get(
                'https://dvmn.org/api/long_polling/',
                headers=headers,
                params=params
            )
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            sleep(3)
        else:
            try:
                response.raise_for_status()
                checks: dict = response.json()
                if not checks.get('status') == 'found':
                    params = {'timestamp': checks['timestamp_to_request']}
                else:
                    logging.info('Lesson info recieved')
                    lesson_info = checks['new_attempts'][0]
                    msg_text = f'У вас проверили работу "{lesson_info["lesson_title"]}"\n\n'
                    if lesson_info['is_negative']:
                        msg_text += 'К сожалению в работе нашлись ошибки\n'
                    else:
                        msg_text += f'Ваша работа принята! Можно приступать к следующему уроку.\n\n'
                    msg_text += f'Cсылка на работу: {lesson_info["lesson_url"]}'
                    bot.send_message(chat_id=chat_id, text=msg_text)
            except Exception:
                logger.info('Bot was interrupted due to error:')
                logger.info(traceback.format_exc())


if __name__ == "__main__":
    main()