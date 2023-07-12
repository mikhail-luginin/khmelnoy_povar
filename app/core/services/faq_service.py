from apps.lk.models import FAQ, FAQTag
from core.validators import validate_field


def faq_all():
    return FAQ.objects.all()


def faq_create(question_title: str | None, question_body: str | None,
               question_tags: list) -> None:
    validate_field(question_title, 'вопрос')
    validate_field(question_body, 'текст вопроса')
    validate_field(question_tags, 'теги')

    faq = FAQ.objects.create(title=question_title, body=question_body)
    faq.tags.set(question_tags)
    faq.save()


def faq_edit(row_id: str | None,
         question_title: str | None, question_body: str | None,
         question_tags: list | None) -> None:
    validate_field(row_id, 'идентификатор')
    validate_field(question_title, 'вопрос')
    validate_field(question_body, 'текст вопроса')
    validate_field(question_tags, 'теги')

    row = FAQ.objects.filter(id=row_id).first()
    if row:
        row.title = question_title
        row.body = question_body
        row.tags.set(question_tags)
        row.save()
    else:
        raise FAQ.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')


def faq_tags_all():
    return FAQTag.objects.all()


def tag_create(name: str) -> FAQTag:
    validate_field(name, 'наименование тега')

    return FAQTag.objects.create(name=name)


def tag_edit(tag_id: int, name: str) -> FAQTag:
    validate_field(tag_id, 'идентификатор тега')
    validate_field(name, 'наименование тега')

    tag = FAQTag.objects.filter(id=tag_id).first()
    if tag:
        tag.name = name
        tag.save()
    else:
        raise FAQTag.DoesNotExist('Тег с указанным идентификатором не найден.')

    return tag
