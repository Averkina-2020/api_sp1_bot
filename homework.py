import logging
import os
import time

from dotenv import load_dotenv

import requests

from telegram import Bot

load_dotenv()


PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

BASE_URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    elif status == 'approved':
        verdict = ('Ревьюеру всё понравилось, '
                   'можно приступать к следующему уроку.')
    else:
        verdict = ('Статус не определён')
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    HEADERS = {
        'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'
    }
    PARAMS = {
        'from_date': current_timestamp
    }
    try:
        homework_statuses = requests.get(
            BASE_URL,
            headers=HEADERS,
            params=PARAMS
        )
    except Exception as e:
        logging.error('Error at %s', 'division', exc_info=e)
        return {}
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    bot_client = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # начальное значение timestamp
    # current_timestamp = 0  # статусы домашних заданий за всё время

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot_client
                )
            current_timestamp = new_homework.get(
                'current_date', current_timestamp
            )  # начало интервала в следующем запросе
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)
            logging.exception('Error')


if __name__ == '__main__':
    main()
