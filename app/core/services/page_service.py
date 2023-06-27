from core import validators

from apps.lk.models import Navbar


def pages_all() -> list[Navbar]:
    return Navbar.objects.all()


def create(page_link: str | None, page_name: str | None, page_app_name: str | None) -> None:
    validators.validate_field(page_link, 'ссылка на страницу')
    validators.validate_field(page_name, 'наименование страницы')
    validators.validate_field(page_app_name, 'наименование приложения')

    Navbar.objects.create(link=page_link, text=page_name, app_name=page_app_name)


def edit(page_id: int | None, page_link: str | None, page_name: str | None, page_app_name: str | None):
    validators.validate_field(page_id, 'идентификатор записи')
    validators.validate_field(page_link, 'ссылка на страницу')
    validators.validate_field(page_name, 'наименование страницы')
    validators.validate_field(page_app_name, 'наименование приложения')

    page = Navbar.objects.filter(id=page_id).first()
    if page:
        page.link = page_link
        page.text = page_name
        page.app_name = page_app_name
        page.save()
