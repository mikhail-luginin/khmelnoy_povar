from core.logs import create_log
from core.telegram import send_message_to_telegram
from core.time import today_date, get_current_time

from core.services.employees import EmployeeService
from core.services.timetable import TimetableService
from core.services.storage import StorageService

from apps.iiko.models import Storage
from apps.bar.models import Timetable, Position, Money, Setting
from apps.lk.models import Employee

from apps.bar.exceptions import EmployeeAlreadyWorkingToday

import datetime


class HomePageService:

    def get_timetable_today(self, bar: Storage) -> list[Timetable]:
        return Timetable.objects.filter(date_at=today_date(), storage=bar)

    def positions_on_storage(self) -> list[dict]:
        rows = []

        employees = Employee.objects.filter(is_deleted=0)

        for position in Position.objects.all().order_by('-priority_id'):
            row = dict()

            if position.args['is_trainee']:
                row['id'] = position.id
                row['name'] = position.name
                row['employees'] = [employee for employee in employees if employee.status == 2]
                row['priority_id'] = position.priority_id
                row['args'] = position.args
            elif position.args['is_called']:
                row['id'] = position.id
                row['name'] = position.name
                row['employees'] = [employee for employee in employees if employee.status == 4 or employee.status == 3]
                row['priority_id'] = position.priority_id
                row['args'] = position.args
            else:
                row['id'] = position.id
                row['name'] = position.name
                row['employees'] = [employee for employee in employees if
                                    employee.job_place in position.linked_jobs.all() if employee.status == 3]
                row['priority_id'] = position.priority_id
                row['args'] = position.args

            rows.append(row)

        return rows

    def timetable_add(self, request):
        storage = StorageService().storage_get(code=request.GET.get('code'))
        bar_setting = Setting.objects.get(storage=storage)

        for position in Position.objects.all():
            employee_id = request.POST.get(f'position[{position.id}]')
            if employee_id and employee_id != '':
                employee = EmployeeService().employee_get(employee_id)
                if not employee:
                    raise Employee.DoesNotExist(f'Указанный сотрудник с идентификатором {employee_id} не найден.')

                check_employee_on_work = TimetableService().is_employee_work_on_date(date_at=today_date(),
                                                                                     employee_id=employee_id)
                if check_employee_on_work:
                    raise EmployeeAlreadyWorkingToday(f'{employee.fio} уже работает сегодня')

                oklad = employee.job_place.gain_shift_oklad_accrual if position.args[
                    'is_usil'] else employee.job_place.main_shift_oklad_accrual

                if position.args['is_trainee']:
                    oklad = 500

                row = Timetable.objects.create(
                    date_at=today_date(),
                    storage=storage,
                    employee=employee,
                    position=position,
                    oklad=oklad
                )
                send_message_to_telegram(chat_id=bar_setting.tg_chat_id,
                                         message=f'{position.name} {employee.fio} вышел(-а) на смену.')
                create_log(owner=f'CRM {storage.name}', entity=employee.fio, row=row,
                           action='create', additional_data='Вышел на смену')

        if self.morning_cashbox_today(storage) is False:
            sum_cash_morning = request.POST.get('sum_cash_morning')
            if sum_cash_morning:
                row = Money.objects.create(date_at=today_date(), storage=storage,
                                           sum_cash_morning=sum_cash_morning, barmen_percent=bar_setting.percent)
                create_log(owner=f'CRM {storage.name}', entity=storage.name, row=row,
                           action='create', additional_data='Смена открыта')

    def morning_cashbox_today(self, storage_id: Storage) -> int | bool:
        row = Money.objects.filter(storage=storage_id, date_at=today_date())
        if row.exists():
            row = row.first()
            return row.sum_cash_morning
        else:
            return False

    def evening_cashbox_previous_day(self, storage: Storage) -> int | str:
        previous_day = (get_current_time() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

        row = Money.objects.filter(storage=storage, date_at=previous_day)
        if row.exists():
            row = row.first()
            if row.sum_cash_end_day:
                return row.sum_cash_end_day
            else:
                return 'Касса вечер предыдущего дня не была заполнена.'
        else:
            return 'Касса вечер предыдущего дня не найдена.'
