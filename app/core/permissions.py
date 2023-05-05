from django.contrib.auth.models import User

from apps.lk.models import Profile, Role, Navbar


class AdministatorAccessMixin:

    def has_access(self, user_id: int) -> bool:
        user = User.objects.get(id=user_id)

        return user.is_superuser == 1


class AccessMixin:
    can_create = None
    can_edit = None
    can_delete = None

    def has_access(self, user_id: int) -> bool:
        if User.objects.get(id=user_id).is_superuser == 1:
            return True

        try:
            user = Profile.objects.get(user_id=user_id)
        except Profile.DoesNotExist:
            Profile.objects.create(user_id=user_id)
            return False

        for user_role in user.roles:
            try:
                role = Role.objects.get(id=user_role.id)
            except Role.DoesNotExist:
                return False

            if role.can_all:
                return True
            else:
                if self.can_create:
                    if role.can_create:
                        return True

                if self.can_edit:
                    if role.can_edit:
                        return True

                if self.can_delete:
                    if role.can_delete:
                        return True

        return False


class CanViewMixin:

    def can_view(self, request) -> bool:
        if request.user.is_superuser == 1:
            return True

        try:
            user = Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
            Profile.objects.create(user_id=request.user.id)
            return False

        for item in user.roles.all():
            try:
                page = Navbar.objects.get(link='/' + request.path.split('/')[1] + '/' + request.path.split('/')[2])
            except Navbar.DoesNotExist:
                return False

            if page in item.can_view:
                return True

        return False

# ToDo: Remake this module and admin app
