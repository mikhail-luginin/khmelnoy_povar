from django.conf import settings

import requests


def send_message_to_telegram(chat_id: str, message: str):
    response = requests.get(
        'https://api.telegram.org/bot' + settings.TELEGRAM_API_KEY + '/sendMessage?chat_id=' + chat_id + '&text=<b>====================</b>\n\n' +
        message + '\n\n<b>====================</b>&parse_mode=html')

    response_json = response.json()
    if response_json['ok'] is False:
        requests.get(
            'https://api.telegram.org/bot' + settings.TELEGRAM_API_KEY + '/sendMessage?chat_id=' + settings.TELEGRAM_CHAT_ID_FOR_ERRORS + '&text=' +
            'Ошибка отправки сообщения: ' + str(response_json['error_code']) + ' | ' + response_json['description'] + '\nID чата: ' + chat_id + '&parse_mode=html')

    return response_json

# ToDo: Celery integration
