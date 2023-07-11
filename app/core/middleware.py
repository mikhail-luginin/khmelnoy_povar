#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect

from core.utils.telegram import send_message_to_telegram


class Process500:

    def __init__(self, get_response):
        self._get_response = get_response

    def __call__(self, request):
        return self._get_response(request)

    def process_exception(self, request, exception):
        import traceback
        trace = traceback.format_exc()
        send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, f'Process500 [<b>{request.path}</b>]\n\n'
                                                                       f'{exception}')
        send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, f'{trace}')
        print(trace)
        messages.error(request, 'Произошла неизвестная ошибка.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
