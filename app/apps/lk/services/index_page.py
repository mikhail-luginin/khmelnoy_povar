from core.services import storage_service
from core.services import employees_service
from core.services import timetable_service
from core.utils.time import today_date


def employees_by_storages() -> list:
    rows = []
    storages = storage_service.storages_all()

    for storage in storages:
        row = {
            "storage": storage,
            "barmens": [],
            "cookers": [],
            "teh": []
        }

        for employee in employees_service.employees_with_deleted_filter(False, storage=storage):
            data = {
                "employee": employee,
                "work_now": timetable_service.is_employee_work_on_date(employee_id=employee.id, date_at=today_date(),
                                                                        get_object=True)
            }

            match employee.job_place.name:
                case 'Бармен':
                    key = 'barmens'
                case 'Повар' | 'Су-Шеф':
                    key = 'cookers'
                case 'Тех. служащий':
                    key = 'teh'
                case _:
                    continue
            row[key].append(data)

        rows.append(row)

    return rows
