from django.conf import settings

import requests


def send_message_to_telegram(chat_id: str, message: str):
    if settings.DEBUG is False:
        if settings.TELEGRAM_CHAT_ID_FOR_ERRORS != chat_id:
            message = '<b>====================</b>\n\n' + message + '\n\n<b>====================</b>'
        response = requests.get(
            'https://api.telegram.org/bot' + settings.TELEGRAM_API_KEY + '/sendMessage?chat_id=' + chat_id + '&text=' +
            message + '&parse_mode=html')

        response_json = response.json()
        if not response_json['ok']:
            requests.get(
                'https://api.telegram.org/bot' + settings.TELEGRAM_API_KEY + '/sendMessage?chat_id=' + settings.TELEGRAM_CHAT_ID_FOR_ERRORS + '&text=' +
                'Ошибка отправки сообщения: ' + str(response_json['error_code']) + ' | ' + response_json[
                    'description'] + '\nID чата: ' + chat_id + '&parse_mode=html')

        return response_json

# ToDo: Celery integration
