from django.conf import settings

from config.celery import app
from core.telegram import send_message_to_telegram

from apps.bar.models import Timetable

from apps.bar.tasks import add_percent_and_premium_to_timetable


@app.task
def calculate_percent_premium_for_all():
    for timetable in Timetable.objects.all():
        add_percent_and_premium_to_timetable(timetable.date_at, timetable.storage_id)

    send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, '<b>[Admin]</b> Проценты и премии обновлены.')
