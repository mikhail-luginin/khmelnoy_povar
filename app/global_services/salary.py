from django.shortcuts import redirect
from django.contrib import messages

from core.time import today_date, get_current_time, monthdelta, get_months

from apps.bar.models import Timetable, Salary, Setting
from apps.iiko.models import Storage
from apps.lk.models import Employee, Fine, Expense

from apps.bar.services.bar_info import get_full_information_of_day, get_main_barmen
from apps.iiko.services.storage import StorageService
from apps.lk.services.catalog import CatalogService

from calendar import monthrange
from typing import List, Literal


class SalaryService:

    def calculate_prepayment_salary_by_timetable_object(self, timetable_object: Timetable) -> dict[
        Literal["oklad", "percent", "premium"], int
    ]:
        percent_num = Setting.objects.first().percent

        percent = 0
        premium = 0

        today_money = get_full_information_of_day(str(timetable_object.date_at), timetable_object.storage)

        if timetable_object.position.args['has_percent']:
            percent += round(today_money['sum_for_percent'] * (percent_num / 100))

        if timetable_object.position.args['has_premium']:
            total_day = today_money['total_day']
            if 80000 <= total_day < 100000:
                premium += 500
            elif 100000 <= total_day < 120000:
                premium += 1000
            elif total_day >= 120000:
                premium += 2000

        return {"oklad": timetable_object.oklad, "percent": percent, "premium": premium}

    def get_money_data_employee(self, request) -> dict:
        data = dict()

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
            session_data.append(SalaryService().calculate_prepayment_salary_by_timetable_object(timetable_object=timetable))

        data['accrued_prepayed_data'] = accrued_prepayed_data
        data['session_data'] = session_data
        data['accrued_month_data'] = accrued_month_data
        data['employee'] = employee
        data['month_name'] = get_months(month)
        data['first_period'] = self.calculate_salary(employee, current_date.year, month, 1)
        data['second_period'] = self.calculate_salary(employee, current_date.year, month, 2)

        return data

    def get_accrued_rows(self, code: str) -> List[dict]:
        rows = []

        bar = StorageService().storage_get(code=code)

        for timetable in Timetable.objects.filter(storage=bar, date_at=today_date()):
            row = dict()

            employee_money_information = self.calculate_prepayment_salary_by_timetable_object(timetable_object=timetable)
            percent = employee_money_information['percent']
            premium = employee_money_information['premium']

            try:
                salary = Salary.objects.get(employee=timetable.employee, type=1, date_at=today_date())
                is_accrued = True
            except Salary.DoesNotExist:
                is_accrued = False

            row['employee'] = timetable.employee
            row['is_accrued'] = is_accrued

            if is_accrued:
                row['oklad'] = salary.oklad
                row['percent'] = salary.percent
                row['premium'] = salary.premium
            else:
                if timetable.position.args['is_usil'] or timetable.position.args['is_called']:
                    row['oklad'] = timetable.oklad
                else:
                    row['oklad'] = 0
                row['percent'] = percent if timetable.position.args['has_percent'] is True else 0
                row['premium'] = premium if timetable.position.args['is_called'] else 0

            row['has_percent'] = timetable.position.args['has_percent']
            row['has_premium'] = timetable.position.args['has_premium']

            rows.append(row)

        return rows

    def _accrue_salary(self, storage: Storage, employee: Employee, salary_type: int, oklad: int, percent: int = 0,
                       premium: int = 0, month: int = 0, period: int = None) -> None:
        Salary.objects.create(
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

        total_sum = oklad + percent + premium
        comment = f'ЗП {salary_type} '
        if salary_type == 2:
            if period == 1:
                period = 'С 1 по 15 число'
            elif period == 2:
                period = 'С 16 по 31 число'
            elif period == 3:
                period = 'Расчет для уволенного'
            comment += get_months(month) + ' ' + period

        Expense.objects.create(
            writer=get_main_barmen(today_date(), storage),
            date_at=today_date(),
            storage=storage,
            expense_type=CatalogService().get_catalog_by_name('Зарплата'),
            expense_source=CatalogService().get_catalog_by_name('Бизнес-карта'),
            payment_receiver=employee.fio,
            sum=total_sum,
            comment=comment
        )

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
        oklad = 0
        percent = 0
        premium = 0
        fines = 0

        if Salary.objects.filter(employee=employee, period=3).exists() is False:
            for timetable in Timetable.objects.filter(employee=employee):
                if timetable.date_at.month == get_current_time().month or timetable.date_at.month == monthdelta(
                        get_current_time(), -1).month:
                    oklad += timetable.oklad

                    employee_money_information = self.calculate_prepayment_salary_by_timetable_object(timetable_object=timetable)
                    percent += employee_money_information['percent']
                    premium += employee_money_information['premium']

                    try:
                        salary = Salary.objects.get(employee=employee, date_at=timetable.date_at)
                        oklad -= salary.oklad
                        percent -= salary.percent
                        premium -= salary.premium
                    except Salary.DoesNotExist:
                        pass

                    try:
                        fine = Fine.objects.get(employee=employee, date_at=timetable.date_at)
                        fines += fine.sum
                    except Fine.DoesNotExist:
                        pass

            return oklad + percent + premium - fines
        else:
            return False

    def get_retired_employee_salary(self, storage: Storage) -> list:
        rows = []

        for employee in Employee.objects.filter(is_deleted=1, storage=storage):
            row = dict()

            salary_sum = self.get_retired_employee_accrue_sum(employee)

            row['employee'] = employee
            row['sum'] = salary_sum

            if salary_sum is not False and salary_sum != 0:
                rows.append(row)

        return rows

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
            fines = 0

            employee_money_information = self.calculate_prepayment_salary_by_timetable_object(timetable_object=timetable)
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
                fine = Fine.objects.get(employee=employee, date_at=timetable.date_at)
                fines += fine.sum
            except Fine.DoesNotExist:
                pass

            calculated_sum += oklad + percent + premium

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

    def get_salary_calculation_rows(self, storage: Storage):
        rows = []

        data = self.data_for_calculate_month_salary()

        for employee in Employee.objects.filter(storage=storage, is_deleted=0):
            row = dict()

            salary_sum = self.calculate_salary(employee, data['year'], data['month'], data['period'])

            row['employee'] = employee
            row['sum'] = salary_sum
            row['is_accrued'] = Salary.objects.filter(period=data['period'],
                                                      month=data['month'],
                                                      date_at__year=data['year'],
                                                      type=2,
                                                      employee=employee).exists()
            if salary_sum != 0:
                rows.append(row)

        return rows

    def get_accrued_salary_month(self, date_at: str, storage: Storage):
        return Salary.objects.filter(date_at=date_at, storage=storage, type=2)
