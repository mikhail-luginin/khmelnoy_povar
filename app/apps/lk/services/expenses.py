from apps.iiko.services.storage import StorageService

from core.time import today_datetime
from .catalog import CatalogService

from apps.lk.models import Expense

from django.shortcuts import redirect
from django.contrib import messages

from typing import List


class ExpenseService:
    model = Expense

    def expenses_all(self) -> List[model]:
        return self.model.objects.all()

    def create_expense(self, request) -> redirect:
        catalog_service = CatalogService()

        date_at = request.POST.get('date_at')
        payment_receiver = request.POST.get('payment_receiver')
        expense_sum = float(request.POST.get('sum'))
        comment = request.POST.get('comment')
        storage_id = int(request.POST.get('storage_id'))

        if not self._check_required_field(request, 'storage_id'):
            return redirect(request.META.get('HTTP_REFERER'))

        storage = StorageService().storage_get(id=storage_id)

        type_id: int = int(request.POST.get('type_id'))

        if not self._check_required_field(request, 'type_id'):
            return redirect(request.META.get('HTTP_REFERER'))

        expense_type_catalog = catalog_service.get_catalog_by_id(type_id)

        source_id: int = int(request.POST.get('source_id'))

        if not self._check_required_field(request, 'source_id'):
            return redirect(request.META.get('HTTP_REFERER'))

        expense_source_catalog = catalog_service.get_catalog_by_id(source_id)

        self.model.objects.create(
            date_at=date_at,
            created_at=today_datetime(),
            writer='Сайт',
            payment_receiver=payment_receiver,
            sum=expense_sum,
            comment=comment,
            storage=storage,
            expense_type=expense_type_catalog,
            expense_source=expense_source_catalog,
        )

        messages.success(request, 'Расход успешно создан :)')
        return redirect('/lk/expenses')

    def _check_required_field(self, request, field_name: str) -> bool:
        input_value = request.POST.get(field_name)
        if not input_value:
            messages.error(request, f'Необходимо заполнить поле {field_name}.')
            return False
        return True

