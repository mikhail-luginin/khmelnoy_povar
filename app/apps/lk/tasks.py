from django.conf import settings

from config.celery import app
from core.telegram import send_message_to_telegram

from apps.bar.models import Timetable, Setting

from apps.bar.tasks import add_percent_and_premium_to_timetable


@app.task
def calculate_percent_premium_for_all():
    for timetable in Timetable.objects.all():
        add_percent_and_premium_to_timetable(timetable.date_at, timetable.storage_id)

    send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, '<b>[Admin]</b> Проценты и премии обновлены.')


@app.task
def bar_actions_telegram_message(storages: list, message: str):
    if 'all' in storages:
        for bar_setting in Setting.objects.all():
            if bar_setting.tg_chat_id:
                send_message_to_telegram(chat_id=bar_setting.tg_chat_id, message=message)
            else:
                send_message_to_telegram(chat_id=settings.TELEGRAM_CHAT_ID_FOR_ERRORS,
                                         message=f'<b>[Admin]</b> ID телеграмм чата не указан для заведения {bar_setting.storage.name}')
    else:
        for storage_id in storages:
            bar_setting = Setting.objects.filter(storage_id=storage_id)
            row = bar_setting.first()
            if row:
                if row.tg_chat_id:
                    send_message_to_telegram(chat_id=row.tg_chat_id, message=message)
                else:
                    send_message_to_telegram(chat_id=settings.TELEGRAM_CHAT_ID_FOR_ERRORS,
                                             message=f'<b>[Admin]</b> ID телеграмм чата не указан для заведения {row.storage.name}')
