from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

from core import exceptions

from apps.iiko.services.storage import StorageService
from apps.lk.services.catalog import CatalogService

from .utils import BaseView
from .services import PurchaserService


class IndexView(BaseView):
    template_name = 'purchaser/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "rows": PurchaserService().get_rows_by_date(date_at=request.GET.get('date_at'),
                                                        storage_id=request.GET.get('storage_id')),
            "storages": StorageService().storages_all()
        })

        return context


class ExpenseCreateView(BaseView):
    template_name = 'purchaser/expense_create.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": StorageService().storages_all(),
            "receivers": CatalogService().get_catalog_by_catalog_type_name_contains(settings.PURCHASER_CATEGORY),
            "types": CatalogService().get_catalog_by_catalog_type_name_contains(settings.EXPENSE_SOURCE_CATEGORY)
        })

        return context

    def post(self, request):
        date_at = request.POST.get('date_at')
        storage_id = request.POST.get('storage_id')
        payment_receiver_id = request.POST.get('payment_receiver_id')
        expense_source_id = request.POST.get('expense_source_id')
        expense_sum = request.POST.get('expense_sum')
        comment = request.POST.get('comment')

        try:
            PurchaserService().expense_create(date_at=date_at, storage_id=storage_id,
                                              payment_receiver_id=payment_receiver_id,
                                              expense_source_id=expense_source_id,
                                              expense_sum=expense_sum, comment=comment)
            messages.success(request, 'Расход успешно записан.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/purchaser')
