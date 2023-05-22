from django.shortcuts import render
from django.views import View

from core.time import today_date


class BaseView(View):
    template_name = None

    def get_context_data(self, request, **kwargs) -> dict:
        date_at = request.GET.get('date_at')
        storage_id = request.GET.get('storage_id')

        context = {
            "date_at": date_at if date_at else today_date(),
            "storage_id": int(storage_id) if storage_id else storage_id
        }

        return context

    def get(self, request):
        return render(request, self.template_name, self.get_context_data(request))
