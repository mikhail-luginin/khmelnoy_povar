from django.shortcuts import render
from django.views import View


class BaseView(View):
    template_name = None

    def get_context_data(self, request, **kwargs):
        context = {}

        return context

    def get(self, request):
        return render(request, self.template_name, context=self.get_context_data(request))
