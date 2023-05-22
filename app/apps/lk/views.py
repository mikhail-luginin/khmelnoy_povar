from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

from core.utils import BaseLkView, ObjectEditMixin, ObjectCreateMixin, ObjectDeleteMixin

from .services import bars
from .services.catalog import CatalogService
from .services.positions import JobsService
from .services.bank import StatementUpdateService, CardService
from .services.money import MoneyService
from .services.employees import EmployeeService
from .services.expenses import ExpenseService
from .services.pays import PaysService
from .services.fines import FineService
from .services.index_page import IndexPageService

from apps.iiko.services.storage import StorageService

from apps.lk.models import Catalog, CatalogType, Card, Expense, Fine, Employee
from apps.bar.models import Position, Timetable, Money, Salary, Pays, Arrival, TovarRequest
from apps.iiko.models import Product, Supplier
from .services.timetable import TimetableService


class IndexView(BaseLkView):
    template_name = 'lk/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "employees_data": IndexPageService().employees_by_storages()
        })

        return context


class CatalogView(BaseLkView):
    template_name = 'lk/catalog/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['catalog_types'] = CatalogService().get_catalog_types()

        return context


class CatalogAddView(ObjectCreateMixin):

    def post(self, request):
        return CatalogService().catalog_create(request)


class CatalogTypeAddView(ObjectCreateMixin):
    model = CatalogType
    success_url = '/lk/catalog'


class CatalogDeleteView(ObjectDeleteMixin):
    model = Catalog
    success_url = '/lk/catalog'


class CatalogTypeDeleteView(ObjectDeleteMixin):
    model = CatalogType
    success_url = '/lk/catalog'


class CatalogEditView(ObjectEditMixin):
    model = Catalog
    template_name = 'lk/catalog/edit.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['types'] = CatalogService().get_catalog_types()
        context['linked_types'] = CatalogService().get_catalog_linked_types(request.GET.get('id'))

        return context

    def post(self, request):
        return CatalogService().catalog_edit(request)


class CatalogTypeEditView(ObjectEditMixin):
    model = CatalogType
    template_name = 'lk/catalog/type_edit.html'
    success_url = '/lk/catalog'


class BarsView(BaseLkView):
    template_name = 'lk/bars.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['bars'] = StorageService().storages_all()

        return context


class BarsSettingsView(BaseLkView):
    template_name = 'lk/bars_settings.html'

    def post(self, request):
        return bars.update_settings(request)


class PositionsView(BaseLkView):
    template_name = 'lk/positions/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['jobs'] = JobsService().jobs_all()

        return context

    def post(self, request):
        return JobsService().position_create(request)


class PositionsEditView(ObjectEditMixin):
    template_name = 'lk/positions/edit.html'
    model = Position

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['jobs'] = JobsService().jobs_all()

        return context

    def post(self, request):
        return JobsService().position_edit(request)


class PositionDeleteView(ObjectDeleteMixin):
    model = Position
    success_url = '/lk/positions'


class JobAddView(BaseLkView):

    def post(self, request):
        job_name = request.POST.get('job-name')
        job_gain_oklad = request.POST.get('job-gain-oklad')
        job_main_oklad = request.POST.get('job-main-oklad')

        try:
            JobsService().job_create(job_name=job_name, job_gain_oklad=job_gain_oklad,
                                     job_main_oklad=job_main_oklad)
            messages.success(request, 'Должность успешно создана.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/lk/positions')


class BankView(BaseLkView):
    template_name = 'lk/bank.html'


@login_required
def bank_update(request):
    return StatementUpdateService().update(request)


class BankPartnersView(BaseLkView):
    template_name = 'lk/partners/index.html'


class BankCardsView(BaseLkView):
    template_name = 'lk/cards/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)

        context['undefined_cards'] = CardService().get_undefined_cards()
        context['cards'] = CardService().cards_all()

        return context


class BankCardCreateView(ObjectCreateMixin):
    template_name = 'lk/cards/create.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['current_card'] = request.GET.get('card')
        context['storages'] = StorageService().storages_all()

        return context

    def post(self, request):
        return CardService().card_create(request)


class BankCardEditView(ObjectEditMixin):
    template_name = 'lk/cards/edit.html'
    model = Card
    success_url = '/lk/bank/cards'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()

        return context


class MoneyView(BaseLkView):
    template_name = 'lk/money/index.html'


@login_required
def update_money(request):
    return MoneyService().update(request)


class MoneyEditView(ObjectEditMixin):
    model = Money

    def post(self, request):
        return MoneyService().money_edit(request)


class TimetableView(BaseLkView):
    template_name = 'lk/timetable/index.html'


class CreateTimetableView(ObjectCreateMixin):
    model = Timetable
    template_name = 'lk/timetable/create.html'
    success_url = '/lk/timetable'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().employees_all(False)
        context['positions'] = JobsService().positions_all()

        return context

    def post(self, request):
        date_at = request.POST.get('date_at')
        employee_id = int(request.POST.get('employee_id'))
        oklad = int(request.POST.get('oklad'))
        position_id = int(request.POST.get('position_id'))
        storage_id = int(request.POST.get('storage_id'))

        if TimetableService().create(date_at=date_at, employee_id=employee_id,
                                     oklad=oklad, position_id=position_id, storage_id=storage_id):
            messages.success(request, 'Запись успешно создана.')
            return redirect('/lk/timetable')


class EditTimetableView(ObjectEditMixin):
    model = Timetable
    template_name = 'lk/timetable/edit.html'
    success_url = '/lk/timetable'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().employees_all(True)
        context['positions'] = JobsService().positions_all()

        return context


class DeleteTimetableView(ObjectDeleteMixin):
    model = Timetable
    success_url = '/lk/timetable'


class ExpensesView(BaseLkView):
    template_name = 'lk/expenses/index.html'


class CreateExpenseView(ObjectCreateMixin):
    template_name = 'lk/expenses/create.html'
    model = Expense
    success_url = '/lk/expenses'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['types'] = CatalogService().get_catalog_by_catalog_type_name_contains('расходы')
        context['sources'] = CatalogService().get_catalog_by_type(settings.EXPENSE_SOURCE_CATEGORY)

        return context

    def post(self, request):
        return ExpenseService().create_expense(request)


class EditExpenseView(ObjectEditMixin):
    template_name = 'lk/expenses/edit.html'
    model = Expense
    success_url = '/lk/expenses'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['types'] = CatalogService().get_catalog_by_catalog_type_name_contains('расходы')
        context['sources'] = CatalogService().get_catalog_by_type(settings.EXPENSE_SOURCE_CATEGORY)

        return context


class DeleteExpenseView(ObjectDeleteMixin):
    model = Expense
    success_url = '/lk/expenses'


class SalaryView(BaseLkView):
    template_name = 'lk/salary/index.html'


class CreateSalaryView(ObjectCreateMixin):
    template_name = 'lk/salary/create.html'
    model = Salary
    success_url = '/lk/salary'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().employees_all(True)

        return context


class EditSalaryView(ObjectEditMixin):
    template_name = 'lk/salary/edit.html'
    model = Salary
    success_url = '/lk/salary'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().employees_all(True)

        return context


class DeleteSalaryView(ObjectDeleteMixin):
    model = Salary
    success_url = '/lk/salary'


class PaysView(BaseLkView):
    template_name = 'lk/pays/index.html'


class CreatePaysView(ObjectCreateMixin):
    template_name = 'lk/pays/create.html'
    model = Pays
    success_url = '/lk/pays'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().employees_all(True)
        context['pays'] = CatalogService().get_catalog_by_catalog_type_name_in_list(
            [settings.PAYIN_CATEGORY, settings.PAYOUT_CATEGORY])

        return context


class EditPaysView(ObjectEditMixin):
    template_name = 'lk/pays/edit.html'
    model = Pays
    success_url = '/lk/pays'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().employees_all(True)
        context['pays'] = CatalogService().get_catalog_by_catalog_type_name_in_list(
            [settings.PAYIN_CATEGORY, settings.PAYOUT_CATEGORY])

        return context


class DeletePaysView(ObjectDeleteMixin):
    model = Pays
    success_url = '/lk/pays'


class FinesView(BaseLkView):
    template_name = 'lk/fines/index.html'


class CreateFineView(ObjectCreateMixin):
    template_name = 'lk/fines/create.html'
    model = Fine
    success_url = '/lk/fines'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().employees_all(True)
        context['reasons'] = CatalogService().get_catalog_by_type(settings.FINE_REASON_CATEGORY)

        return context


class EditFinesView(ObjectEditMixin):
    template_name = 'lk/fines/edit.html'
    model = Fine
    success_url = '/lk/fines'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().employees_all(True)
        context['reasons'] = CatalogService().get_catalog_by_type(settings.FINE_REASON_CATEGORY)

        return context


class DeleteFineView(ObjectDeleteMixin):
    model = Fine
    success_url = '/lk/fines'


class EmployeesView(BaseLkView):
    template_name = 'lk/employees/index.html'


class CreateEmployeeView(ObjectCreateMixin):
    template_name = 'lk/employees/create.html'
    model = Employee

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['jobs'] = JobsService().jobs_all()

        return context

    def post(self, request):
        return EmployeeService().employee_create(request)


class EditEmployeeView(ObjectEditMixin):
    template_name = 'lk/employees/edit.html'
    model = Employee
    success_url = '/lk/employees'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['jobs'] = JobsService().jobs_all()

        return context


class DissmissEmployeeView(BaseLkView):

    def get(self, request):
        return EmployeeService().dismiss(request)


class ReturnToWorkEmployeeView(BaseLkView):

    def get(self, request):
        return EmployeeService().return_to_work(request)


class ArrivalsView(BaseLkView):
    template_name = 'lk/arrivals/index.html'


# ToDo: Refactor this

class ArrivalCreateView(ObjectCreateMixin):
    template_name = 'lk/arrivals/create.html'
    model = Arrival
    success_url = '/lk/tovar/arrivals'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['products'] = Product.objects.filter(category__name__in=[settings.TOVAR_BEER_CATEGORY, settings.TOVAR_DRINKS_CATEGORY])
        context['suppliers'] = Supplier.objects.all()
        context['payment_types'] = Catalog.objects.filter(catalog_types__name=settings.EXPENSE_SOURCE_CATEGORY)

        return context


class ArrivalEditView(ObjectEditMixin):
    template_name = 'lk/arrivals/edit.html'
    model = Arrival
    success_url = '/lk/tovar/arrivals'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['products'] = Product.objects.filter(
            category__name__in=[settings.TOVAR_BEER_CATEGORY, settings.TOVAR_DRINKS_CATEGORY])
        context['suppliers'] = Supplier.objects.all()
        context['payment_types'] = Catalog.objects.filter(catalog_types__name=settings.EXPENSE_SOURCE_CATEGORY)

        return context


class ArrivalDeleteView(ObjectDeleteMixin):
    model = Arrival
    success_url = '/lk/tovar/arrivals'


class TovarRequestsView(BaseLkView):
    template_name = 'lk/tovar_requests/index.html'


class TovarRequestEditView(ObjectEditMixin):
    pass


class TovarRequestDeleteView(ObjectDeleteMixin):
    model = TovarRequest
    success_url = '/lk/tovar/requests'
