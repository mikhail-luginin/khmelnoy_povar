from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render, redirect
from django.views import View

from .permissions import CanViewMixin, AccessMixin
from .time import today_datetime
from .logs import create_log
from .profile import get_profile, get_navbar


class BaseLkView(LoginRequiredMixin, CanViewMixin, View):
    login_url = '/login/'
    template_name = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.id is not None:
            if not self.can_view(request) and request.path != '/lk/' and 'admin' not in request.path:
                raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, request, **kwargs) -> dict:
        context = dict()

        context['profile'] = get_profile(request)
        context['navbar'] = get_navbar(request.user.id)

        context.update(**kwargs)

        return context

    def get(self, request):
        return render(request, self.template_name, self.get_context_data(request))


class ObjectCreateMixin(AccessMixin, BaseLkView):
    model = None
    template_name = None
    success_url = None
    can_create = 1

    def get(self, request):
        return render(request, self.template_name, self.get_context_data(request))

    def dispatch(self, request, *args, **kwargs):
        if request.user.id is not None:
            if not self.has_access(request.user.id):
                raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)


class ObjectDeleteMixin(AccessMixin, BaseLkView):
    model = None
    success_url = None
    can_delete = 1

    def dispatch(self, request, *args, **kwargs):
        if request.user.id is not None:
            if not self.has_access(request.user.id):
                raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        try:
            row = self.model.objects.get(id=request.GET.get('id'))
        except self.model.DoesNotExist:
            messages.error(request, 'Объекта с данным ID не существует :(')
            return redirect(self.success_url)

        row.delete()
        create_log(request.user.username, request.path, f'Удаление записи в модели {str(self.model)}')

        messages.success(request, 'Объект успешно удален :)')
        return redirect(self.success_url)


class ObjectEditMixin(AccessMixin, BaseLkView):
    model = None
    template_name = None
    success_url = None
    can_edit = 1

    def get(self, request):
        try:
            row = self.model.objects.get(id=request.GET.get('id'))
        except self.model.DoesNotExist:
            messages.error(request, 'Объект с данным ID не найден :(')
            return redirect('/' if self.success_url is None else self.success_url)

        context = self.get_context_data(request, row=row)

        return render(request, self.template_name, context)

    def dispatch(self, request, *args, **kwargs):
        if request.user.id is not None:
            if not self.has_access(request.user.id):
                raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)
