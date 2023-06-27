from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect

from core import exceptions

from .utils import BaseView, ObjectEditMixin, ObjectDeleteMixin
from .exceptions import PasswordDontMatchError

from core.services import role_service, user_service, page_service

from apps.lk.models import Role, Navbar, Profile


class IndexView(BaseView):
    template_name = 'admin/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "roles": role_service.roles_all(),
            "pages": page_service.pages_all(),
            "users": user_service.users_all()
        })

        return context


class RoleCreateView(BaseView):

    def post(self, request):
        role_name = request.POST.get('role-name')
        can_all = bool(request.POST.get('can-all'))
        can_create = bool(request.POST.get('can-create'))
        can_edit = bool(request.POST.get('can-edit'))
        can_delete = bool(request.POST.get('can-delete'))
        can_view = request.POST.getlist('can-view')

        try:
            role_service.create(role_name=role_name, can_create=can_create, can_all=can_all, can_view=can_view,
                                 can_edit=can_edit, can_delete=can_delete)
            messages.success(request, 'Роль успешно создана.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/admin')


class RoleEditView(ObjectEditMixin):
    template_name = 'admin/edit_role.html'
    model = Role

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "pages": page_service.pages_all()
        })

        return context

    def post(self, request):
        role_id = request.GET.get('id')
        role_name = request.POST.get('name')
        can_all = bool(request.POST.get('can-all'))
        can_create = bool(request.POST.get('can-create'))
        can_edit = bool(request.POST.get('can-edit'))
        can_delete = bool(request.POST.get('can-delete'))
        can_view = request.POST.getlist('can-view')

        try:
            role_service.edit(role_id=role_id, role_name=role_name, can_create=can_create, can_all=can_all,
                               can_view=can_view, can_edit=can_edit, can_delete=can_delete)
            messages.success(request, 'Роль успешно отредактирована.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, self.model.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/admin')


class RoleDeleteView(ObjectDeleteMixin):
    model = Role


class PageCreateView(BaseView):

    def post(self, request):
        page_link = request.POST.get('page-link')
        page_name = request.POST.get('page-text')
        page_app_name = request.POST.get('page-app-name')

        try:
            page_service.create(page_link=page_link, page_name=page_name, page_app_name=page_app_name)
            messages.success(request, 'Страница успешно создана.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/admin')


class PageEditView(ObjectEditMixin):
    template_name = 'admin/edit_page.html'
    model = Navbar

    def post(self, request):
        page_id = request.GET.get('id')
        page_link = request.POST.get('page-link')
        page_name = request.POST.get('page-text')
        page_app_name = request.POST.get('page-app-name')

        try:
            page_service.edit(page_id=page_id, page_link=page_link, page_name=page_name, page_app_name=page_app_name)
            messages.success(request, 'Страница успешно отредактирована.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, self.model.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/admin')


class PageDeleteView(ObjectDeleteMixin):
    model = Navbar


class UserCreateView(BaseView):

    def post(self, request):
        username = request.POST.get('username')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        role = request.POST.get('role')

        try:
            user_service.create(username=username, first_name=first_name, last_name=last_name,
                                 email=email, password=password, confirm_password=confirm_password, role=role)
            messages.success(request, 'Пользователь успешно создан.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, PasswordDontMatchError) as error:
            messages.error(request, error)

        return redirect('/admin')


class UserEditView(ObjectEditMixin):
    model = Profile
    template_name = 'admin/edit_user.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "roles": role_service.roles_all()
        })

        return context

    def post(self, request):
        user_id = request.GET.get('id')
        role = request.POST.get('role')

        try:
            user_service.edit(user_id=user_id, role=role)
            messages.success(request, 'Пользователь успешно отредактирован.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/admin')


class UserDeleteView(ObjectDeleteMixin):
    model = User
