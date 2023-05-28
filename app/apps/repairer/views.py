from django.contrib import messages
from django.shortcuts import redirect

from core import exceptions
from core.utils import BaseLkView
from .models import Malfunction

from .services import RepairerService


class IndexView(BaseLkView):
    template_name = 'repairer/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "rows": RepairerService().malfunctions_get(storage_id=request.GET.get('storage_id'))
        })

        return context


class MalfunctionComplete(BaseLkView):

    def get(self, request):
        malfunction_id = request.GET.get('id')

        try:
            RepairerService().malfunction_repaired(malfunction_id=malfunction_id)
            messages.success(request, 'Ваш ответ был успешно отправлен.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Malfunction.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/repairer')
