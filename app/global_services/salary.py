from django.db.models import Sum
from django.shortcuts import redirect
from django.contrib import messages

from core.logs import create_log
from core.time import today_date, get_current_time, monthdelta, get_months

from apps.bar.models import Timetable, Salary, Money
from apps.iiko.models import Storage
from apps.lk.models import Employee, Fine

from apps.bar.services.bar_info import get_full_information_of_day, get_bar_settings
from apps.iiko.services.storage import StorageService

from calendar import monthrange
from typing import Literal


class SalaryService:

    def calculate_prepayment_salary_by_timetable_object(self, timetable_object: Timetable) -> dict[
        Literal["oklad", "percent", "premium"], int
    ]:
        try:
            percent_num = Money.objects.get(storage_id=timetable_object.storage_id, date_at=timetable_object.date_at).barmen_percent
        except Money.DoesNotExist:
            percent_num = get_bar_settings(storage_id=timetable_object.storage_id).percent

        percent = 0
        premium = 0

        today_money = get_full_information_of_day(str(timetable_object.date_at), timetable_object.storage)
        if 'error' not in today_money:
            if timetable_object.position.args['has_percent']:
                percent += round(today_money['sum_for_percent'] * (percent_num / 100))

            if timetable_object.position.args['has_premium']:
                date = str(timetable_object.date_at).split('-')
                year = int(date[0])
                month = int(date[1])
                if year >= 2023 and month >= 5:
                    total_day = today_money['total_day']
                    if 80000 <= total_day < 100000:
                        premium += 500
                    elif 100000 <= total_day < 120000:
                        premium += 1000
                    elif total_day >= 120000:
                        premium += 2000
                else:
                    total_day = today_money['total_day'] if timetable_object.employee.job_place.name != 'Бармен' else \
                        today_money['sum_for_percent']
                    if 60000 <= total_day < 70000:
                        premium += 200
                    elif 70000 <= total_day < 100000:
                        premium += 500
                    elif total_day >= 100000:
                        premium += 1000

            return {"oklad": timetable_object.oklad, "percent": percent, "premium": premium}
        else:
            return {"oklad": 0, "percent": 0, "premium": 0}

    def get_money_data_employee(self, request) -> dict:
        data = dict()
        data['amount_main_shifts'] = 0
        data['amount_gain_shifts'] = 0

        employee_code = request.GET.get('employee_code')
        previous = request.GET.get('previous')

        employee = Employee.objects.get(code=employee_code)
        data['previous'] = False
        current_date = get_current_time()

        if not previous:
            month = current_date.month
        else:
            month = monthdelta(current_date, -1).month
            data['previous'] = True

        accrued_prepayed_data = []
        accrued_month_data = []
        session_data = []

        entire_salary_data = []
        work_months = []

        for timetable in Timetable.objects.filter(employee=employee).order_by('-date_at'):
            row = dict()
            row['year'] = timetable.date_at.year
            row['month'] = timetable.date_at.month
            if row not in work_months:
                work_months.append(row)

        for date in work_months:
            row = {'year': date['year'], 'month': get_months(date['month']),
                   'received_salary': 0, 'accrued_salary': 0}

            for salary in Salary.objects.filter(date_at__month=date['month'], date_at__year=date['year'], employee=employee, type=1):
                row['received_salary'] += int(salary.get_total_sum())

            for salary in Salary.objects.filter(date_at__month=date['month'], date_at__year=date['year'],employee=employee, type=2):
                row['received_salary'] += salary.oklad

            for timetable in Timetable.objects.filter(date_at__month=date['month'], date_at__year=date['year'],employee=employee).order_by('-date_at'):
                calculated_salary = SalaryService().calculate_prepayment_salary_by_timetable_object(
                    timetable_object=timetable)
                row['accrued_salary'] += calculated_salary['oklad'] + calculated_salary['percent'] + calculated_salary['premium'] - timetable.fine

            entire_salary_data.append(row)

        for salary in Salary.objects.filter(date_at__month=month, employee=employee, type=1).order_by('-date_at'):
            row = dict()
            row['salary'] = salary
            row['total'] = salary.get_total_sum()
            accrued_prepayed_data.append(row)

        for salary in Salary.objects.filter(date_at__month=month, employee=employee, type=2).order_by('-date_at'):
            row = dict()
            row['salary'] = salary
            row['month_name'] = salary.get_month_name()
            row['period_name'] = salary.get_period_name()
            accrued_month_data.append(row)

        for timetable in Timetable.objects.filter(date_at__month=month, employee=employee).order_by('-date_at'):
            calculated_salary = SalaryService().calculate_prepayment_salary_by_timetable_object(
                timetable_object=timetable)

            oklad = calculated_salary['oklad']
            percent = calculated_salary['percent']
            premium = calculated_salary['premium']

            row = dict()
            row['date_at'] = timetable.date_at
            row['oklad'] = oklad
            row['percent'] = percent
            row['premium'] = premium
            row['total'] = oklad + percent + premium - timetable.fine
            row['fine'] = timetable.fine
            session_data.append(row)

            if timetable.position.args["is_usil"]:
                data['amount_gain_shifts'] += 1
            else:
                data['amount_main_shifts'] += 1

        data['accrued_prepayed_data'] = accrued_prepayed_data
        data['session_data'] = session_data
        data['accrued_month_data'] = accrued_month_data
        data['employee'] = employee
        data['month_name'] = get_months(month)
        data['first_period'] = self.calculate_salary(employee, current_date.year, month, 1)
        data['second_period'] = self.calculate_salary(employee, current_date.year, month, 2)
        data['entire_salary_data'] = entire_salary_data

        return data

    def get_accrued_rows(self, code: str) -> dict:
        data = {
            "rows": [],
            "total_sum": 0,
            "issued_sum": 0,
            "left_sum": 0
        }

        bar = StorageService().storage_get(code=code)

        for timetable in Timetable.objects.filter(storage=bar, date_at=today_date()):
            row = dict()

            employee_money_information = self.calculate_prepayment_salary_by_timetable_object(
                timetable_object=timetable)
            percent = employee_money_information['percent']
            premium = employee_money_information['premium']

            try:
                salary = Salary.objects.get(employee=timetable.employee, type=1, date_at=today_date())
                is_accrued = True
            except Salary.DoesNotExist:
                salary = None
                is_accrued = False

            row['employee'] = timetable.employee
            row['position'] = timetable.position
            row['is_accrued'] = is_accrued

            if is_accrued:
                row['oklad'] = salary.oklad
                row['percent'] = salary.percent
                row['premium'] = salary.premium
                data['issued_sum'] += salary.oklad + salary.percent + salary.premium
            else:
                if timetable.position.args['is_called']:
                    if timetable.position.args['is_usil']:
                        row['oklad'] = timetable.employee.job_place.gain_shift_oklad_accrual
                    else:
                        row['oklad'] = timetable.employee.job_place.main_shift_oklad_accrual
                else:
                    if timetable.position.args['is_usil']:
                        row['oklad'] = timetable.employee.job_place.gain_shift_oklad_receiving
                    else:
                        row['oklad'] = timetable.employee.job_place.main_shift_oklad_receiving
                row['percent'] = percent if timetable.position.args['has_percent'] is True else 0
                row['premium'] = premium if timetable.position.args['is_called'] else 0

            row['has_percent'] = timetable.position.args['has_percent']
            row['has_premium'] = timetable.position.args['has_premium']
            data['total_sum'] += row['oklad'] + row['percent'] + row['premium']

            data['rows'].append(row)
            data['left_sum'] = data['total_sum'] - data['issued_sum']

        return data

    def _accrue_salary(self, storage: Storage, employee: Employee, salary_type: int, oklad: int, percent: int = 0,
                       premium: int = 0, month: int = 0, period: int = None) -> None:
        row = Salary.objects.create(
            date_at=today_date(),
            employee=employee,
            storage=storage,
            type=salary_type,
            oklad=oklad,
            percent=percent,
            premium=premium,
            month=month,
            period=period
        )

        additional_data = ''
        match salary_type:
            case 1:
                additional_data = 'Зарплата аванс получена'
            case 2:
                additional_data = f'Зарплата расчет за {get_months(month)} {row.get_period_name()} получена'
            case 3:
                additional_data = 'Зарплата при увольнении получена'

        create_log(owner=f'CRM {storage.name}', entity=employee.fio, row=row,
                   action='create', additional_data=additional_data)

    def accrue_salary_prepayment(self, request) -> redirect:
        bar = StorageService().storage_get(code=request.GET.get('code'))
        employee = None

        for timetable in Timetable.objects.filter(storage=bar, date_at=today_date()):
            if timetable.employee.code == request.GET.get('employee_code'):
                if Salary.objects.filter(employee=timetable.employee, date_at=today_date(), type=1).exists() is False:
                    oklad = request.POST.get(f'salary[{timetable.employee.code}][oklad]')
                    percent = request.POST.get(f'salary[{timetable.employee.code}][percent]')
                    premium = request.POST.get(f'salary[{timetable.employee.code}][premium]')

                    percent = percent if percent is not None and len(percent) > 0 else 0
                    premium = premium if premium is not None and len(premium) > 0 else 0

                    self._accrue_salary(bar, timetable.employee, 1, int(oklad), int(percent), int(premium))
                    employee = timetable.employee.fio
                else:
                    messages.error(request, f'{timetable.employee.fio} уже получил зарплату :(')
                    return redirect('/bar/salary?code=' + request.GET.get('code'))

        messages.success(request, f'Сотрудник {employee} успешно получил зарплату :)')
        return redirect('/bar/salary?code=' + request.GET.get('code'))

    def accrue_month_salary(self, request):
        bar = StorageService().storage_get(code=request.GET.get('code'))

        data = self.data_for_calculate_month_salary()

        employee = Employee.objects.get(id=request.POST.get('employee_id'))

        if Salary.objects.filter(employee=employee, month=data['month'], period=data['period'],
                                 date_at__year=data['year']).exists():
            messages.error(request,
                           f'{employee.fio} уже получил зарплату за {data["period"]} период {data["month"]} :(')
            return redirect(request.META.get('HTTP_REFERER'))

        salary_sum = self.calculate_salary(employee, data['year'], data['month'], data['period'])

        if salary_sum == 0:
            messages.error(request, 'Нельзя получить нулевую зарплату :(')
            return redirect(request.META.get('HTTP_REFERER'))

        self._accrue_salary(storage=bar, employee=employee, salary_type=2,
                            oklad=salary_sum, month=data['month'], period=data['period'])

        messages.success(request, f'{employee.fio} успешно получил зарплату :)')
        return redirect(request.META.get('HTTP_REFERER'))

    def get_retired_employee_accrue_sum(self, employee: Employee) -> int | bool:
        calculated_sum = 0

        if not Salary.objects.filter(employee=employee, period=3).exists():
            current_datetime = get_current_time()
            previous_month_datetime = monthdelta(get_current_time(), -1)

            calculated_sum += self.calculate_salary(employee=employee,
                                                    year=current_datetime.year,
                                                    month=current_datetime.month,
                                                    period=1)
            calculated_sum += self.calculate_salary(employee=employee,
                                                    year=current_datetime.year,
                                                    month=current_datetime.month,
                                                    period=2)
            calculated_sum += self.calculate_salary(employee=employee,
                                                    year=previous_month_datetime.year,
                                                    month=previous_month_datetime.month,
                                                    period=1)
            calculated_sum += self.calculate_salary(employee=employee,
                                                    year=previous_month_datetime.year,
                                                    month=previous_month_datetime.month,
                                                    period=2)

            received_sum_obj = Salary.objects.filter(employee=employee,
                                                     date_at__month=current_datetime.month,
                                                     date_at__year=current_datetime.year,
                                                     month=previous_month_datetime.month,
                                                     type=2).aggregate(total_sum=Sum('oklad'))['total_sum']
            received_sum_objj = Salary.objects.filter(employee=employee,
                                                      date_at__month=current_datetime.month,
                                                      date_at__year=current_datetime.year,
                                                      month=current_datetime.month,
                                                      type=2).aggregate(total_sum=Sum('oklad'))['total_sum']
            received_sum_objjj = Salary.objects.filter(employee=employee,
                                                       date_at__month=previous_month_datetime.month,
                                                       date_at__year=previous_month_datetime.year,
                                                       month=previous_month_datetime.month,
                                                       type=2).aggregate(total_sum=Sum('oklad'))['total_sum']
            received_sum = received_sum_obj if received_sum_obj else 0
            received_summ = received_sum_objj if received_sum_objj else 0
            received_summm = received_sum_objjj if received_sum_objjj else 0

            return calculated_sum - received_sum - received_summ - received_summm
        else:
            return False

    def get_retired_employee_salary(self, storage: Storage) -> dict:
        data = {
            "rows": [],
            "total_sum": 0
        }

        for employee in Employee.objects.filter(is_deleted=1, storage=storage):
            row = dict()

            salary_sum = self.get_retired_employee_accrue_sum(employee)

            row['employee'] = employee
            row['sum'] = salary_sum

            data['total_sum'] += salary_sum

            if salary_sum is not False and salary_sum != 0:
                data['rows'].append(row)

        return data

    def accrue_retired_employee_salary(self, request):
        employee_code = request.GET.get('employee_code')
        code = request.GET.get('code')

        storage = StorageService().storage_get(code=code)

        try:
            employee = Employee.objects.get(code=employee_code)
        except Employee.DoesNotExist:
            messages.error(request, 'Сотрудник не найден :(')
            return redirect('/bar/salary/retired_employees?code=' + code)

        try:
            Salary.objects.get(employee=employee, period=3)
            messages.error(request, 'Данный сотрудник уже получил зарплату при увольнении :(')
        except Salary.DoesNotExist:
            self._accrue_salary(storage, employee, 2, oklad=self.get_retired_employee_accrue_sum(employee),
                                month=get_current_time().month, period=3)
            messages.success(request, f'{employee.fio} успешно получил зарплату :)')

        return redirect('/bar/salary/retired_employees?code=' + code)

    def calculate_salary(self, employee: Employee, year: int, month: int, period: int) -> int:
        day_gte = None
        day_lte = None

        if period == 1:
            day_gte = 1
            day_lte = 15
        elif period == 2:
            day_gte = 16
            day_lte = monthrange(year, month)[1]

        calculated_sum = 0

        for timetable in Timetable.objects.filter(date_at__day__gte=day_gte,
                                                  date_at__day__lte=day_lte,
                                                  date_at__year=year,
                                                  date_at__month=month,
                                                  employee=employee):
            oklad = timetable.oklad
            percent = 0
            premium = 0
            fine = 0

            employee_money_information = self.calculate_prepayment_salary_by_timetable_object(
                timetable_object=timetable)
            percent += employee_money_information['percent']
            premium += employee_money_information['premium']

            try:
                salary = Salary.objects.get(employee=employee, date_at=timetable.date_at, type=1)
                oklad -= salary.oklad
                percent -= salary.percent
                premium -= salary.premium
            except Salary.DoesNotExist:
                pass

            try:
                fines = Fine.objects.filter(employee=employee, date_at=timetable.date_at)
                for row in fines:
                    fine += row.sum
            except Fine.DoesNotExist:
                pass

            calculated_sum += oklad + percent + premium - fine

        return calculated_sum

    def data_for_calculate_month_salary(self) -> dict:
        current_date = get_current_time()
        month = monthdelta(current_date, -1).month
        year = current_date.year - 1 if month == 1 else current_date.year
        period = None

        if current_date.day >= 26:
            month += 1

        if 11 <= current_date.day <= 25:
            period = 2
        elif current_date.day >= 26 or current_date.day <= 10:
            period = 1

        return dict(month=month, period=period, year=year, month_name=get_months(month))

    def get_salary_calculation_rows(self, storage: Storage) -> dict:
        data = {
            "rows": [],
            "total_sum": 0,
            "issued_sum": 0,
            "left_sum": 0
        }

        data_for_calculate = self.data_for_calculate_month_salary()

        for employee in Employee.objects.filter(storage=storage, is_deleted=0):
            row = dict()

            salary_sum = self.calculate_salary(employee, data_for_calculate['year'],
                                               data_for_calculate['month'], data_for_calculate['period'])
            is_accrued = Salary.objects.filter(period=data_for_calculate['period'],
                                               month=data_for_calculate['month'],
                                               date_at__year=data_for_calculate['year'],
                                               type=2,
                                               employee=employee).exists()

            row['employee'] = employee
            row['sum'] = salary_sum
            row['is_accrued'] = is_accrued
            data['total_sum'] += salary_sum

            if is_accrued:
                data['issued_sum'] += salary_sum

            if salary_sum != 0:
                data["rows"].append(row)

        data['left_sum'] = data['total_sum'] - data['issued_sum']

        return data

    def get_accrued_salary_month(self, date_at: str, storage: Storage):
        return Salary.objects.filter(date_at=date_at, storage=storage, type=2)
