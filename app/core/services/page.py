from core import validators

from apps.lk.models import Navbar


class PageService:
    model = Navbar

    def pages_all(self) -> list[model]:
        return self.model.objects.all()

    def create(self, page_link: str | None, page_name: str | None, page_app_name: str | None) -> None:
        validators.validate_field(page_link, 'ссылка на страницу')
        validators.validate_field(page_name, 'наименование страницы')
        validators.validate_field(page_app_name, 'наименование приложения')

        self.model.objects.create(link=page_link, text=page_name, app_name=page_app_name)

    def edit(self, page_id: int | None, page_link: str | None, page_name: str | None, page_app_name: str | None):
        validators.validate_field(page_id, 'идентификатор записи')
        validators.validate_field(page_link, 'ссылка на страницу')
        validators.validate_field(page_name, 'наименование страницы')
        validators.validate_field(page_app_name, 'наименование приложения')

        page = self.model.objects.filter(id=page_id)
        if page.exists():
            page = page.first()
            page.link = page_link
            page.text = page_name
            page.app_name = page_app_name
            page.save()
