from django.contrib.auth.models import User

from core import validators

from apps.lk.models import Profile

from apps.admin.exceptions import PasswordDontMatchError


class UserService:
    user_model = User
    profile_model = Profile

    def users_all(self) -> list[profile_model]:
        return self.profile_model.objects.all()

    def create(self, username: str | None, first_name: str | None, last_name: str | None,
               email: str | None, password: str | None, confirm_password: str | None, role: int | None):
        validators.validate_field(username, 'имя пользователя')
        validators.validate_field(first_name, 'имя')
        validators.validate_field(last_name, 'фамилия')
        validators.validate_field(email, 'почта')
        validators.validate_field(password, 'пароль')
        validators.validate_field(confirm_password, 'подтверждение пароля')
        validators.validate_field(role, 'роль')

        if password != confirm_password:
            raise PasswordDontMatchError('Пароли не сходятся.')

        user = self.user_model.objects.create(username=username, first_name=first_name, last_name=last_name, email=email)
        user.set_password(password)
        user.save()
        self.profile_model.objects.create(user_id=user.id, role_id=role)

    def edit(self, user_id: int | None, role: int | None):
        validators.validate_field(user_id, 'идентификатор записи')
        validators.validate_field(role, 'роль')

        profile = self.profile_model.objects.filter(user_id=user_id)
        if profile.exists():
            profile = profile.first()
            profile.role_id = role
            profile.tg_id = ''
            profile.save()
