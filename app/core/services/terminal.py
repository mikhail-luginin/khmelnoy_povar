from core.services.api import IikoService

from apps.iiko.models import Terminal

from .storage import StorageService

import xml.etree.ElementTree as ET


class TerminalService:

    def terminal_by_uuid(self, uuid: str) -> Terminal | None:
        return Terminal.objects.filter(terminal_uuid=uuid).first()

    def update(self) -> None:
        text = IikoService().get_terminals()
        terminals_xml = ET.fromstring(text)

        storage_service = StorageService()
        for terminal_dto in terminals_xml.findall('terminalDto'):
            group_info = terminal_dto.find('groupInfo')

            names = [terminal_dto.findtext('name'), terminal_dto.findtext('computerName')]
            if group_info:
                names.append(group_info.findtext('name'))

            for storage in storage_service.storages_all():
                if storage.name in names:
                    terminal_id = terminal_dto.findtext('id')
                    if not self.terminal_by_uuid(terminal_id):
                        Terminal.objects.create(terminal_uuid=terminal_id, storage_id=storage.id)
            else:
                if group_info:
                    storage = storage_service.storage_get(name__contains=group_info.findtext('name'))
                    if storage:
                        terminal_id = group_info.findtext('id')
                        if not self.terminal_by_uuid(terminal_id):
                            Terminal.objects.create(terminal_uuid=terminal_id, storage_id=storage.id)
