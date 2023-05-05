from django.shortcuts import redirect
from django.contrib import messages

from apps.iiko.models import Storage
from apps.iiko.services.storage import StorageService
from apps.repairer.models import Malfunction

from typing import List


class MalfunctionService:
    model = Malfunction

    def malfunction_create(self, request):
        storage = StorageService().storage_get(code=request.GET.get('code'))

        photo = request.FILES.get('malfunction-photo')
        fault_object = request.POST.get('fault-object')
        description = request.POST.get('malfunction-description')

        self.model.objects.create(storage=storage,
                                  photo=photo,
                                  fault_object=fault_object,
                                  description=description)

        messages.success(request, 'Неисправность успешно занесена в список :)')
        return redirect(request.META.get('HTTP_REFERER'))

    def malfunctions_get(self, storage: Storage) -> List[model]:
        return Malfunction.objects.filter(storage=storage)
