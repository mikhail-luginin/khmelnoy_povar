import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('khmelnoy_povar')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'iiko-stoplist': {
        'task': 'apps.iiko.tasks.iiko_stoplist_items',
        'schedule': crontab(minute='*/15')
    }
}
