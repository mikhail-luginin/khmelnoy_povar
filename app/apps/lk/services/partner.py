from django.contrib import messages
from django.shortcuts import redirect

from apps.lk.models import Partner

from typing import List


class PartnerService:
    partner_model = Partner

    def get_partners(self) -> List[partner_model]:
        return self.partner_model.objects.all()

    def partner_edit(self, request) -> redirect:
        row_id = request.GET.get('id')
        friendly_name = request.POST.get('friendly_name')
        expense_type = request.POST.get('expense_type')
        storage_id = request.POST.get('storage_id')

        try:
            row = self.partner_model.objects.get(id=row_id)
        except Partner.DoesNotExist:
            messages.error(request, 'Запись не найдена :(')
            return redirect('/lk/bank/partners')
        row.friendly_name = friendly_name
        row.expense_type.set(expense_type)
        row.storage.set(storage_id)

        row.save()
        messages.success(request, 'Контрагент успешно отредактирован :)')
        return redirect('/lk/bank/partners')