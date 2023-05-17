from typing import List

from core.time import today_date
from core.total_values import get_total_expenses_by_date_and_storage
from global_services.salary import SalaryService

from .utils import BaseView, ObjectDeleteMixin, TovarRequestMixin, ArrivalMixin, InventoryMixin, DataLogsMixin

from .services.index import HomePageService
from .services.expenses import ExpensesPageService
from .services.end_day import complete_day
from .services.malfunctions import MalfunctionService
from .services.fines import get_fines_on_storage_by_month
from .services.bar_info import get_full_information_of_day

from apps.bar.models import Timetable, TovarRequest, Arrival, Pays, Setting, Salary, Money
from apps.lk.models import Expense, Fine

from apps.lk.services import catalog, positions, employees

from django.conf import settings

from django.db.models import Sum

from ..iiko.models import Storage


class IndexView(BaseView):
    template_name = 'bar/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = HomePageService().get_timetable_today(context['bar'])
        context['positions'] = HomePageService().positions_on_storage()
        context['is_morning_cashbox_filled'] = HomePageService().validate_today_morning_cashbox(context['bar'])
        context['evening_cashbox_previous_day'] = HomePageService().evening_cashbox_previous_day(context['bar'])

        return context

    def post(self, request):
        return HomePageService().timetable_add(request)


class TimetableDeleteView(ObjectDeleteMixin):
    model = Timetable


class ExpensesView(BaseView):
    template_name = 'bar/expenses.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = ExpensesPageService().get_expenses_today(context['bar'])
        context['expenses_types'] = catalog.CatalogService().get_catalog_by_type(settings.EXPENSE_TYPE_CATEGORY)
        context['expenses_sources'] = catalog.CatalogService().get_catalog_by_type(settings.EXPENSE_SOURCE_CATEGORY)
        context['timetable'] = HomePageService().get_timetable_today(context['bar'])
        context['expenses'] = dict(nal=get_total_expenses_by_date_and_storage(context['bar'], context['date'], False),
                                   bn=get_total_expenses_by_date_and_storage(context['bar'], context['date'], True))
        context['payin_types'] = catalog.CatalogService().get_catalog_by_type(settings.PAYIN_CATEGORY)
        context['payout_types'] = catalog.CatalogService().get_catalog_by_type(settings.PAYOUT_CATEGORY)
        context['pays_rows'] = Pays.objects.filter(date_at=today_date(), storage=context['bar'])
        context['bar_setting'] = Setting.objects.get(id=1)

        return context

    def post(self, request):
        return ExpensesPageService().create_expense(request)


class ExpenseDeleteView(ObjectDeleteMixin):
    model = Expense


class OtherView(BaseView):
    template_name = 'bar/other.html'


class SalaryView(BaseView):
    template_name = 'bar/salary/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['data'] = SalaryService().get_accrued_rows(request.GET.get('code'))
        context['salaries'] = Salary.objects.filter(storage=context['bar'], date_at=today_date(), type=1).annotate(
            total_sum=Sum('oklad') + Sum('percent') + Sum('premium')
        )

        return context

    def post(self, request):
        return SalaryService().accrue_salary_prepayment(request)


class SalaryForRetiredEmployeesView(BaseView):
    template_name = 'bar/salary/retired_employees.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = SalaryService().get_retired_employee_salary(context['bar'])

        return context


def salary_for_retired_employee_accrue_view(request):
    return SalaryService().accrue_retired_employee_salary(request)


class EndDayView(BaseView):
    template_name = 'bar/end_day.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['information'] = get_full_information_of_day(today_date(), context['bar'])

        return context

    def post(self, request):
        return complete_day(request)


class AddEmployeeView(BaseView):
    template_name = 'bar/add_employee.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['jobs'] = positions.JobsService().jobs_all()

        return context

    def post(self, request):
        return employees.EmployeeService().employee_create(request)


class TovarRequestBeerView(TovarRequestMixin):
    category = settings.TOVAR_BEER_CATEGORY


class TovarRequestBarView(TovarRequestMixin):
    category = settings.TOVAR_DRINKS_CATEGORY


class TovarRequestProductsView(TovarRequestMixin):
    category = settings.TOVAR_PRODUCTS_CATEGORY


class TovarRequestHozView(TovarRequestMixin):
    category = settings.TOVAR_HOZ_CATEGORY


class TovarRequestBoxView(TovarRequestMixin):
    category = settings.TOVAR_BOX_CATEGORY


class TovarRequestDeleteView(ObjectDeleteMixin):
    model = TovarRequest


class ArrivalBeerView(ArrivalMixin):
    category = settings.TOVAR_BEER_CATEGORY


class ArrivalDrinkView(ArrivalMixin):
    category = settings.TOVAR_DRINKS_CATEGORY


class ArrivalDeleteView(ObjectDeleteMixin):
    model = Arrival


class SalaryCalculationView(BaseView):
    template_name = 'bar/salary/calculation.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = SalaryService().get_salary_calculation_rows(context['bar'])
        context['data_for_calculate_month_salary'] = SalaryService().data_for_calculate_month_salary()
        context['records'] = SalaryService().get_accrued_salary_month(today_date(), context['bar'])

        return context

    def post(self, request):
        return SalaryService().accrue_month_salary(request)


class EmployeeView(BaseView):
    template_name = 'bar/employee.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['data'] = SalaryService().get_money_data_employee(request)

        return context


class InventoryBarView(InventoryMixin):
    category_name = settings.TOVAR_DRINKS_CATEGORY


class InventoryWareView(InventoryMixin):
    category_name = settings.TOVAR_WARE_CATEGORY


class MalfunctionsView(BaseView):
    template_name = 'bar/malfunctions.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = MalfunctionService().malfunctions_get(context['bar'])

        return context

    def post(self, request):
        return MalfunctionService().malfunction_create(request)


class PaysAddView(BaseView):

    def post(self, request):
        return ExpensesPageService().pays_create(request)


class PaysDeleteView(ObjectDeleteMixin):
    model = Pays


class FinesView(DataLogsMixin):
    template_name = 'bar/fines.html'
    model = Fine
    type = 2

    def _prepare_rows(self, storage: Storage, obj: int | None) -> List[model]:
        return get_fines_on_storage_by_month(storage=storage, month=obj)

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['fines'] = self._prepare_rows(storage=context.get('bar'), obj=request.GET.get('date'))
        return context


class TimetableDataLogView(DataLogsMixin):
    model = Timetable
    template_name = 'bar/data_logs/timetable.html'
    type = 1


class ArrivalsDataLogView(DataLogsMixin):
    model = Arrival
    template_name = 'bar/data_logs/arrivals.html'
    type = 1


class EndDayDataLogView(DataLogsMixin):
    model = Money
    template_name = 'bar/data_logs/end_day.html'
    type = 1
