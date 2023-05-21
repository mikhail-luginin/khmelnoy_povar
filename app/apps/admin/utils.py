from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from core.exceptions import FieldNotFoundError


class BaseView(LoginRequiredMixin, View):
    template_name = None

    def get_context_data(self, request, **kwargs) -> dict:
        context = {

        }

        return context

    def get(self, request):
        if request.user.is_superuser:
            return render(request, self.template_name, self.get_context_data(request))
        else:
            return redirect('/lk')


class ObjectDeleteMixin(BaseView):
    model = None

    def get(self, request):
        if request.user.is_superuser:
            row_id = request.GET.get('id')

            qs = self.model.objects.filter(id=row_id)
            if qs.exists():
                row = qs.first()
                row.delete()
                messages.success(request, 'Запись успешно удалена.')
            else:
                messages.error(request, 'Запись с указанным идентификатором не найдена.')

            return redirect('/admin')
        else:
            return redirect('/lk')


class ObjectEditMixin(BaseView):
    model = None

    def _get_row(self, row_id: int | None) -> model:
        row = self.model.objects.filter(id=row_id)
        if row.exists():
            return row.first()
        raise FieldNotFoundError(f'Запись с указанным идентификатором не найдена.')

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "row": self._get_row(request.GET.get('id'))
        })

        return context
