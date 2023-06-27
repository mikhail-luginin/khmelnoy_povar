from django.contrib.auth.models import User

from core import validators

from apps.lk.models import Profile

from apps.admin.exceptions import PasswordDontMatchError


def users_all() -> list[Profile]:
    return Profile.objects.all()


def create(username: str | None, first_name: str | None, last_name: str | None,
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

    user = User.objects.create(username=username, first_name=first_name, last_name=last_name, email=email)
    user.set_password(password)
    user.save()
    Profile.objects.create(user_id=user.id, role_id=role)


def edit(user_id: int | None, role: int | None):
    validators.validate_field(user_id, 'идентификатор записи')
    validators.validate_field(role, 'роль')

    profile = Profile.objects.filter(user_id=user_id).first()
    if profile:
        profile.role_id = role
        profile.tg_id = ''
        profile.save()
