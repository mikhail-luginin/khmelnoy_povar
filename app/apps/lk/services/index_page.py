from apps.iiko.services.storage import StorageService
from apps.lk.services.employees import EmployeeService
from apps.lk.services.timetable import TimetableService
from core.time import today_date


class IndexPageService:

    def employees_by_storages(self) -> list:
        rows = []
        storages = StorageService().storages_all()

        for storage in storages:
            row = {
                "storage": storage,
                "employees": []
            }

            for employee in EmployeeService().employees_all(False, storage=storage):
                data = {
                    "employee": employee,
                    "work_now": TimetableService().is_employee_work_on_date(employee_id=employee.id, date_at=today_date())
                }
                row['employees'].append(data)

            rows.append(row)

        return rows
