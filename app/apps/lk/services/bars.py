from django.shortcuts import redirect
from django.contrib import messages

from apps.bar.models import Setting, TelegramChats


def update_settings(request) -> redirect:
    percent = request.POST.get('percent', None)
    try:
        settings = Setting.objects.get(id=1)
    except Setting.DoesNotExist:
        settings = None

    if settings:
        settings.percent = percent
        settings.save()

    else:
        Setting.objects.create(percent=percent).save()

    messages.success(request, 'Настройки успешно обновлены :)')
    return redirect('/lk/bars')
