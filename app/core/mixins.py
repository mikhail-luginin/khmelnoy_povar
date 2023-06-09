from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render, redirect
from django.views import View

from apps.lk.models import Navbar

from .exceptions import FieldNotFoundError
from .permissions import CanViewMixin, AccessMixin
from .utils.profile import profile_by_request
from .utils.time import today_date


class BaseLkView(LoginRequiredMixin, CanViewMixin, View):
    login_url = '/login/'
    template_name = None

    def dispatch(self, request, *args, **kwargs):
        if request.user.id and not request.user.is_superuser:
            if not self.can_view(request) and request.path != '/lk/':
                raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, request, **kwargs) -> dict:
        context = {
            "profile": profile_by_request(request),
            "navbar": Navbar.objects.all(),
            "date": today_date()
        }
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
        if request.user.id and not request.user.is_superuser:
            if not self.has_access(request.user.id):
                raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)


class ObjectDeleteMixin(AccessMixin, BaseLkView):
    model = None
    success_url = None
    can_delete = 1

    def dispatch(self, request, *args, **kwargs):
        if request.user.id and not request.user.is_superuser:
            if not self.has_access(request.user.id):
                raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        row = self.model.objects.filter(id=request.GET.get('id')).first()
        if not row:
            messages.error(request, 'Объекта с данным ID не существует :(')
            return redirect(self.success_url)

        row.delete()

        messages.success(request, 'Объект успешно удален :)')
        return redirect(self.success_url)


class ObjectEditMixin(AccessMixin, BaseLkView):
    model = None
    template_name = None
    success_url = None
    can_edit = 1

    def _get_row(self, row_id):
        row = self.model.objects.filter(id=row_id).first()
        if row:
            return row
        raise FieldNotFoundError(f'Запись с указанным идентификатором не найдена.')

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['row'] = self._get_row(request.GET.get('id'))

        return context

    def get(self, request):
        try:
            context = self.get_context_data(request)
        except FieldNotFoundError as error:
            messages.error(request, error)
            return redirect(request.META.get('HTTP_REFERER'))
        return render(request, self.template_name, context)

    def dispatch(self, request, *args, **kwargs):
        if request.user.id and not request.user.is_superuser:
            if not self.has_access(request.user.id):
                raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)
