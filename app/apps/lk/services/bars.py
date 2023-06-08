from apps.bar.models import Setting, EndDayQuestions

from core import validators


class BarSettingService:
    model = Setting

    def settings_edit(self, storage_id: int, percent: str, tg_chat_id: str) -> None:
        validators.validate_field(percent, 'процент')
        validators.validate_field(tg_chat_id, 'ID телеграм чата')

        setting = self.model.objects.filter(storage_id=storage_id)
        if setting.exists():
            setting = setting.first()
            setting.percent = percent
            setting.tg_chat_id = tg_chat_id
            setting.save()
        else:
            raise self.model.DoesNotExist('Настройки с указанным идентификатором заведения не найдены.')

    def questions_for_link(self) -> list[EndDayQuestions]:
        return EndDayQuestions.objects.all()

    def link_question_to_storage(self, question_text: str,  storage_id: int, question_id: int) -> None:
        if question_id == '':
            question = EndDayQuestions.objects.filter(text=question_text)
        else:
            question = EndDayQuestions.objects.filter(id=question_id)

        if question.exists():
            question_id = question.first().id
        else:
            validators.validate_field(question_text, 'текст вопроса')
            question_id = EndDayQuestions.objects.create(text=question_text).id

        setting = self.model.objects.filter(storage_id=storage_id)
        if setting.exists():
            setting = setting.first()
            setting.end_day_questions.add(question_id)
        else:
            raise self.model.DoesNotExist('Настройки с указанным идентификатором заведения не найдены.')

    def get_setting_by_storage_id(self, storage_id: int) -> model | None:
        return self.model.objects.filter(storage_id=storage_id).first()

    def get_question_on_end_day_by_storage_id(self, storage_id: int) -> dict:
        questions_query_set = self.get_setting_by_storage_id(storage_id=storage_id).end_day_questions
        data = {
            "questions_list": [],
            "questions_count": questions_query_set.count()
        }

        i = 0
        for question in questions_query_set.all():
            i += 1
            data['questions_list'].append({
                "id": i,
                "text": question.text
            })

        return data
