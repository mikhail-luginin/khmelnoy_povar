from django.shortcuts import redirect
from django.contrib import messages

from apps.bar.models import Setting


def update_settings(request) -> redirect:
    percent = request.POST.get('percent', None)
    chat_type_id = request.POST.get('chat-type-id', None)
    chat_id = request.POST.get('chat-id', None)

    settings = Setting.objects.first()
    if settings:
        if not percent:
            settings.percent = percent

        if chat_type_id and chat_type_id != '-1' and chat_id:
            settings.telegram_chats[chat_type_id] = chat_id

        settings.save()

        messages.success(request, 'Настройки успешно обновлены :)')
        return redirect('/lk/bars')

    messages.error(request, 'Настройки не были найдены :(')
    return redirect('/lk/bars')
