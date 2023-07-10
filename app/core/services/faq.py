from apps.lk.models import FAQ
from core.validators import validate_field


class FAQService:
    def create(self, question_title: str | None, question_body: str | None) -> None:
        validate_field(question_title, 'вопрос')
        validate_field(question_body, 'текст вопроса')

        FAQ.objects.create(title=question_title, body=question_body)

    def edit(self, row_id: str | None, question_title: str | None, question_body: str | None) -> None:
        validate_field(row_id, 'идентификатор')
        validate_field(question_title, 'вопрос')
        validate_field(question_body, 'текст вопроса')

        row = FAQ.objects.filter(id=row_id).first()

        if row:
            row.title = question_title
            row.body = question_body
            row.save()
        else:
            raise FAQ.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')
