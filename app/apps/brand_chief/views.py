from django.contrib import messages
from django.shortcuts import redirect

from core import exceptions
from core.utils import BaseLkView

from core.services.storage import StorageService
from apps.bar.services.malfunctions import MalfunctionService
from core.services.index_page import IndexPageService
from core.services.item_deficit import ItemDeficitService


class IndexView(BaseLkView):
    template_name = 'brand_chief/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "employees_data": IndexPageService().employees_by_storages()
        })

        return context


class MalfunctionsView(BaseLkView):
    template_name = 'brand_chief/malfunctions.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = MalfunctionService().all()
        context['storages'] = StorageService().storages_all()

        return context

    def post(self, request):
        storage_id = request.POST.get('storage_id')
        photo = request.FILES.get('malfunction-photo')
        fault_object = request.POST.get('fault-object')
        description = request.POST.get('malfunction-description')

        try:
            MalfunctionService().malfunction_create(storage_id=storage_id, photo=photo,
                                                    fault_object=fault_object, description=description)
            messages.success(request, 'Неисправность успешно занесена в список.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/brand_chief/malfunctions')


class ItemDeficitView(BaseLkView):
    template_name = 'brand_chief/item_deficit.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)

        storage_id = request.GET.get('storage_id')
        if storage_id:
            need_items = ItemDeficitService().deficit_by_storage(storage_id=storage_id)
        else:
            need_items = ItemDeficitService().all()

        context.update({
            "is_filter": storage_id,
            "need_items": need_items,
            "storages": StorageService().storages_all()
        })

        return context

    def post(self, request):
        item = request.POST.get('need_item')
        amount = request.POST.get('amount_need_item')
        storage_id = request.POST.get('storage_id')

        try:
            ItemDeficitService().create(storage_id=storage_id, item=item, amount=amount)
            messages.success(request, 'Заявка на нехватку успешно создана.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, str(error))

        return redirect('/brand_chief/item_deficit')
    
    
class SendMessageView(BaseLkView):
    template_name = "brand_chief/send_message.html"
    
    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": StorageService().storages_all()
        })
        
        return context
