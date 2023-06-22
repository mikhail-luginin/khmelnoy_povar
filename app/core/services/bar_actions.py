from apps.lk.models import Profile

from apps.lk.tasks import bar_actions_telegram_message


class BarActionsService:

    def send_message_on_bar(self, storages: list, message: str, profile: Profile) -> None:
        bar_actions_telegram_message.delay(storages=storages,
                                           message=f'{message}\n\n<b>{profile.user.first_name} '
                                                   f'{profile.user.last_name}</b>')
