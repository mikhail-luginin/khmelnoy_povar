from apps.iiko.services.storage import StorageService
from apps.lk.services.employees import EmployeeService
from apps.lk.services.timetable import TimetableService
from core.utils.time import today_date


class IndexPageService:

    def employees_by_storages(self) -> list:
        rows = []
        storages = StorageService().storages_all()

        for storage in storages:
            row = {
                "storage": storage,
                "barmens": [],
                "cookers": [],
                "teh": []
            }

            for employee in EmployeeService().employees_all(False, storage=storage):
                data = {
                    "employee": employee,
                    "work_now": TimetableService().is_employee_work_on_date(employee_id=employee.id, date_at=today_date(),
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
