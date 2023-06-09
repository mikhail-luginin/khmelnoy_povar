from django.contrib import messages
from django.shortcuts import redirect
from django.conf import settings

from core import exceptions

from apps.lk.models import Expense

from core.services import storage_service, catalog_service

from .utils import BaseView
from .services import PurchaserService
from .exceptions import DateIsNotEqualCurrentError, RowWasNotCreatedByPurchaser


class IndexView(BaseView):
    template_name = 'purchaser/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "rows": PurchaserService().get_rows_by_date(date_at=request.GET.get('date_at'),
                                                        storage_id=request.GET.get('storage_id')),
            "storages": storage_service.storages_all(),
            "data": PurchaserService().get_money_data(date_at=request.GET.get('date_at'),
                                                      storage_id=request.GET.get('storage_id'))
        })

        return context


class ExpenseCreateView(BaseView):
    template_name = 'purchaser/expense_create.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "receivers": catalog_service.get_catalog_by_catalog_type_name_contains(settings.PURCHASER_CATEGORY),
            "types": catalog_service.get_catalog_by_catalog_type_name_contains(settings.EXPENSE_SOURCE_CATEGORY)
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


class DeleteRowView(BaseView):

    def get(self, request):
        try:
            PurchaserService().delete(row_id=request.GET.get('id'))
            messages.success(request, 'Запись успешно удалена.')
        except (DateIsNotEqualCurrentError, RowWasNotCreatedByPurchaser, Expense.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/purchaser')
