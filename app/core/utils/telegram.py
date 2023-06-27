from django.conf import settings

from core.tasks import send_message_to_telegram_task


def send_message_to_telegram(chat_id: str, message: str):
    if settings.DEBUG is False:
        send_message_to_telegram_task.delay(chat_id=chat_id, message=message)
