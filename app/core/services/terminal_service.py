from core.services.api.iiko import IikoService

from apps.iiko.models import Terminal

from . import storage_service as storage_service

import xml.etree.ElementTree as ET


def terminal_by_uuid(uuid: str) -> Terminal | None:
    return Terminal.objects.filter(terminal_uuid=uuid).first()

def update() -> None:
    text = IikoService().get_terminals()
    terminals_xml = ET.fromstring(text)

    for terminal_dto in terminals_xml.findall('terminalDto'):
        group_info = terminal_dto.find('groupInfo')

        names = [terminal_dto.findtext('name'), terminal_dto.findtext('computerName')]
        if group_info:
            names.append(group_info.findtext('name'))

        for storage in storage_service.storages_all():
            if storage.name in names:
                terminal_id = terminal_dto.findtext('id')
                if not terminal_by_uuid(terminal_id):
                    Terminal.objects.create(terminal_uuid=terminal_id, storage_id=storage.id)
        else:
            if group_info:
                storage = storage_service.storage_get(name__contains=group_info.findtext('name'))
                if storage:
                    terminal_id = group_info.findtext('id')
                    if not terminal_by_uuid(terminal_id):
                        Terminal.objects.create(terminal_uuid=terminal_id, storage_id=storage.id)
