import datetime

from apps.iiko.models import Storage
from apps.lk.services.employees import EmployeeService
from core.time import today_date, get_current_time
from .bar_info import get_main_barmen

from apps.bar.models import Timetable, Position, Money
from apps.lk.models import Employee

from apps.iiko.services.storage import StorageService

from django.shortcuts import redirect
from django.contrib import messages

from typing import List


class HomePageService:

    def get_timetable_today(self, bar: Storage) -> List[Timetable]:
        return Timetable.objects.filter(date_at=today_date(), storage=bar)

    def positions_on_storage(self) -> List[dict]:
        rows = []

        employees = Employee.objects.filter(is_deleted=0)

        for position in Position.objects.all().order_by('-priority_id'):
            row = dict()

            row['id'] = position.id
            row['name'] = position.name
            row['employees'] = [employee for employee in employees if employee.job_place in position.linked_jobs.all()]
            row['priority_id'] = position.priority_id
            row['args'] = position.args

            rows.append(row)

        return rows

    def timetable_add(self, request) -> redirect:
        error = False
        storage = StorageService().storage_get(code=request.GET.get('code'))

        for position in Position.objects.all():
            employee_id = request.POST.get(f'position[{position.id}]')
            if employee_id is not None and employee_id != '':

                employee = EmployeeService().employee_get(employee_id)
                if employee is None:
                    messages.error(request, 'Сотрудника не существует :(')
                    error = True
                    continue

                check_employee_on_work = Timetable.objects.filter(date_at=today_date(),
                                                                  storage=storage,
                                                                  employee=employee).exists()
                if check_employee_on_work:
                    messages.error(request, 'Данный сотрудник уже работает :(')
                    error = True
                    continue

                Timetable.objects.create(
                    date_at=today_date(),
                    storage=storage,
                    employee=employee,
                    position=position,
                    oklad=position.args['oklad']
                )

                # today_main_barmen = get_main_barmen(today_date(), storage)
                # username_for_logs = 'Бармен не указан' if not today_main_barmen else today_main_barmen.fio
                # create_log(username_for_logs, request.path, 'Добавление сотрудника', comment=f'{storage.name} | {employee.fio}', is_bar=True)

        if self.validate_today_morning_cashbox(storage) is False:
            sum_cash_morning = request.POST.get('sum_cash_morning')
            if sum_cash_morning:
                if not get_main_barmen(today_date(), storage):
                    messages.error(request, 'Основной бармен не указан.')
                    return redirect('/bar?code=' + storage.code)
                Money.objects.create(date_at=today_date(), storage=storage,
                                     sum_cash_morning=sum_cash_morning)

        if not error:
            messages.success(request, 'Данные смены успешно обновлены :)')
        return redirect('/bar?code=' + request.GET.get('code'))

    def validate_today_morning_cashbox(self, storage_id: Storage) -> int | bool:
        try:
            return Money.objects.get(storage=storage_id, date_at=today_date()).sum_cash_morning
        except Money.DoesNotExist:
            return False

    def evening_cashbox_previous_day(self, storage: Storage):
        previous_day = (get_current_time() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        try:
            sum_cash_end_day = Money.objects.get(storage=storage, date_at=previous_day).sum_cash_end_day
            return sum_cash_end_day if sum_cash_end_day else 'Касса вечер предыдущего дня не была заполнена.'
        except Money.DoesNotExist:
            return 'Касса вечер предыдущего дня не найдена.'
