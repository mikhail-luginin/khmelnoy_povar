from django.contrib import messages
from django.shortcuts import redirect

from core import exceptions
from core.mixins import BaseLkView

from apps.lk.models import ItemDeficit
from core.services.item_deficit import ItemDeficitService

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


class ItemDeficitView(BaseLkView):
    template_name = 'repairer/item_deficit.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "rows": ItemDeficitService().all()
        })

        return context


class ItemDeficitSendView(BaseLkView):

    def post(self, request):
        context = self.get_context_data(request)

        request_id = request.GET.get('id')

        try:
            receive_status = ItemDeficitService().send(request_id=request_id, user=context.get('profile'),
                                                       sended_amount=request.POST.get('sended_amount'),
                                                       comment=request.POST.get('comment'))
            if receive_status:
                messages.success(request, 'Статус успешно обновлен.')
            else:
                messages.error(request, 'Этот запрос уже обработан.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, ItemDeficit.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/repairer/item_deficit')
