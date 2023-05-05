from django.shortcuts import redirect
from django.contrib import messages

from .telegram import send_message_to_telegram

from django.conf import settings


class Process500:

    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        return self._get_response(request)

    def process_exception(self, request, exception):
        send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, f'Process500 [<b>{request.path}</b>]\n\n{exception}')
        messages.error(request, 'Произошла неизвестная ошибка.')
        return redirect(request.META.get('HTTP_REFERER'))
