from django.contrib.auth.models import User

from apps.lk.models import Profile


class AdministatorAccessMixin:

    def has_access(self, user_id: int) -> bool:
        user = User.objects.filter(id=user_id)
        if user.exists():
            user = user.first()
            return user.is_superuser == 1
        else:
            return False


class AccessMixin:
    can_create = None
    can_edit = None
    can_delete = None

    def has_access(self, user_id: int) -> bool:
        profile = Profile.objects.filter(user_id=user_id)
        if profile.exists():
            profile = profile.first()
            user = profile.user
            role = profile.role

            if user.is_superuser:
                return True

            if self.can_create:
                return role.can_create
            if self.can_edit:
                return role.can_edit
            if self.can_delete:
                return role.can_delete

        return False


class CanViewMixin:

    def can_view(self, request) -> bool:
        profile = Profile.objects.filter(user_id=request.user.id)
        if profile.exists():
            profile = profile.first()
            role = profile.role

            page_url = request.path

            if 'create' in page_url:
                page_url = page_url.replace('/create', '')
            elif 'edit' in page_url:
                page_url = page_url.replace('/edit', '')
            elif 'delete' in page_url:
                page_url = page_url.replace('/delete', '')

            for page in role.can_view.all():
                if page.link == page_url:
                    return True

        return False
