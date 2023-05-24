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
def bar_actions_telegram_message(storage: int | str, message: str):
    if storage == 'all':
        for bar_setting in Setting.objects.all():
            send_message_to_telegram(chat_id=bar_setting.tg_chat_id, message=message)
    else:
        bar_setting = Setting.objects.filter(storage_id=storage)
        if bar_setting.exists():
            row = bar_setting.first()
            send_message_to_telegram(chat_id=row.tg_chat_id, message=message)
