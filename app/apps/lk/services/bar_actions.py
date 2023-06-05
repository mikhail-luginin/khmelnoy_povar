from django.conf import settings

from apps.lk.models import Profile

from apps.lk.tasks import bar_actions_telegram_message
from core.telegram import send_message_to_telegram


class BarActionsService:

    def send_message_on_bar(self, storage: int | str, message: str, profile: Profile) -> None:
        bar_actions_telegram_message.delay(storage=storage, 
                                           message=f'{message}\n\n{profile.user.first_name} {profile.user.last_name}')

        send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, '<b>[Admin]</b> Сообщение отправлено в чат(-ы).')
