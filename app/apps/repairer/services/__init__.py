from typing import List

from django.shortcuts import redirect
from django.contrib import messages

from apps.repairer.models import Malfunction
from apps.iiko.models import Storage
from apps.iiko.services.storage import StorageService


def malfunctions_get(request) -> List[Malfunction]:
    storage_id = request.GET.get('id')

    if not storage_id:
        return Malfunction.objects.all()

    try:
        storage = StorageService().storage_get(id=storage_id)
    except Storage.DoesNotExist:
        messages.error(request, 'Данное заведение не найдено.')
        return Malfunction.objects.all()

    return Malfunction.objects.filter(storage=storage)


def malfunction_complete(request) -> redirect:
    malfunction_id = request.GET.get('id')
    url = request.META.get('HTTP_REFERER')

    if not malfunction_id:
        messages.error(request, 'ID не заполнено.')
        return redirect(url)

    try:
        malfunction = Malfunction.objects.get(id=malfunction_id)
    except Malfunction.DoesNotExist:
        messages.error(request, 'Запись не найдена.')
        return redirect(url)

    malfunction.status = 1
    malfunction.save()
    return redirect(url)
