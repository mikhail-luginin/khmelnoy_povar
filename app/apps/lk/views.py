from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

from core.time import get_months
from core.utils import BaseLkView, ObjectEditMixin, ObjectCreateMixin, ObjectDeleteMixin
from core import exceptions

from .services import bars
from .services.bar_actions import BarActionsService
from .services.item_deficit import ItemDeficitService
from .services.salary import SalaryService
from .services.catalog import CatalogService
from .services.positions import JobsService
from .services.bank import StatementUpdateService, CardService, PartnerService
from .services.money import MoneyService
from .services.employees import EmployeeService
from .services.expenses import ExpenseService
from .services.pays import PaysService
from .services.fines import FineService
from .services.index_page import IndexPageService
from .services.timetable import TimetableService
from .tasks import calculate_percent_premium_for_all

from apps.iiko.services.storage import StorageService

from apps.lk.models import Catalog, CatalogType, Card, Expense, Fine, Employee, ItemDeficit, Partner
from apps.bar.models import Position, Timetable, Money, Salary, Pays, Arrival, TovarRequest, Setting
from apps.iiko.models import Product, Supplier
from apps.repairer.models import Malfunction


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
        name = request.POST.get('catalog-name')
        linked = request.POST.getlist('linked')

        try:
            if CatalogService().catalog_create(name, linked):
                messages.success(request, 'Запись успешно добавлена в справочник.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, CatalogType.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/catalog')


class CatalogTypeAddView(ObjectCreateMixin):
    model = CatalogType
    success_url = '/lk/catalog'

    def post(self, request):
        name = request.POST.get('name')

        try:
            if CatalogService().catalog_type_create(name):
                messages.success(request, 'Тип каталога успешно создан.')
        except (exceptions.FieldCannotBeEmptyError, exceptions.FieldNotFoundError) as error:
            messages.error(request, error)

        return redirect('/lk/catalog')


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
        row_id = request.GET.get('id')
        name = request.POST.get('name')
        linked = request.POST.getlist('linked')

        try:
            if CatalogService().catalog_edit(row_id=row_id, name=name, linked=linked):
                messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, CatalogType.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/catalog')


class CatalogTypeEditView(ObjectEditMixin):
    model = CatalogType
    template_name = 'lk/catalog/type_edit.html'

    def post(self, request):
        row_id = request.GET.get('id')
        name = request.POST.get('name')

        try:
            if CatalogService().catalog_type_edit(row_id=row_id, name=name):
                messages.success(request, 'Тип справочника успешно отредактирован.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, CatalogType.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/catalog')


class BarsView(BaseLkView):
    template_name = 'lk/bars.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['bars'] = Setting.objects.all()

        return context


class BarsSettingsView(ObjectEditMixin):
    template_name = 'lk/bars_settings.html'
    model = Setting

    def post(self, request):
        storage_id = request.GET.get('id')
        percent = request.POST.get('percent')
        tg_chat_id = request.POST.get('chat-id')

        try:
            bars.settings_edit(storage_id=storage_id, percent=percent, tg_chat_id=tg_chat_id)
            messages.success(request, 'Настройки бара успешно обновлены')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Setting.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/bars')


class PositionsView(BaseLkView):
    template_name = 'lk/positions/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['jobs'] = JobsService().jobs_all()

        return context

    def post(self, request):
        position_name = request.POST.get('position-name')
        position_oklad = request.POST.get('position-oklad')
        position_all_storages = bool(request.POST.get('position-all-storages'))
        position_is_usil = bool(request.POST.get('position-is-usil'))
        position_is_called = bool(request.POST.get('position-is-calling'))
        position_is_trainee = bool(request.POST.get('position-is-trainee'))
        position_has_percent = bool(request.POST.get('position-has-percent'))
        position_has_premium = bool(request.POST.get('position-has-premium'))
        position_job_ids = request.POST.getlist('job_id')
        priority_id = request.POST.get('priority-id')

        try:
            JobsService().position_create(position_oklad=position_oklad, position_is_usil=position_is_usil,
                                          position_name=position_name, position_is_trainee=position_is_trainee,
                                          position_is_called=position_is_called,
                                          position_all_storages=position_all_storages,
                                          position_has_percent=position_has_percent,
                                          position_has_premium=position_has_premium,
                                          position_job_ids=position_job_ids, priority_id=priority_id)
            messages.success(request, 'Позиция успешно создана.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/lk/positions')


class PositionsEditView(ObjectEditMixin):
    template_name = 'lk/positions/edit.html'
    model = Position

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['jobs'] = JobsService().jobs_all()

        return context

    def post(self, request):
        position_id = request.GET.get('id')
        position_name = request.POST.get('position-name')
        position_oklad = request.POST.get('position-oklad')
        position_all_storages = bool(request.POST.get('position-all-storages'))
        position_is_usil = bool(request.POST.get('position-is-usil'))
        position_is_called = bool(request.POST.get('position-is-calling'))
        position_is_trainee = bool(request.POST.get('position-is-trainee'))
        position_has_percent = bool(request.POST.get('position-has-percent'))
        position_has_premium = bool(request.POST.get('position-has-premium'))
        position_job_ids = request.POST.getlist('job_id')
        priority_id = request.POST.get('priority-id')

        try:
            JobsService().position_edit(position_id=position_id, position_name=position_name,
                                        position_is_trainee=position_is_trainee, position_is_called=position_is_called,
                                        position_job_ids=position_job_ids, position_is_usil=position_is_usil,
                                        position_has_premium=position_has_premium,
                                        position_has_percent=position_has_percent,
                                        position_all_storages=position_all_storages, position_oklad=position_oklad,
                                        priority_id=priority_id)
            messages.success(request, 'Позиция успешно отредактирована')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Position.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/positions')


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


class BankPartnerEditView(ObjectEditMixin):
    template_name = 'lk/partners/edit.html'
    model = Partner

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "types": CatalogService().get_catalog_by_type(type_name=settings.EXPENSE_TYPE_CATEGORY),
            "storages": StorageService().storages_all()
        })

        return context

    def post(self, request):
        partner_id = request.GET.get('id')
        friendly_name = request.POST.get('friendly_name')
        expense_types = request.POST.getlist('expense_types')
        storages = request.POST.getlist('storages')

        try:
            PartnerService().edit(partner_id=partner_id, friendly_name=friendly_name,
                                  expense_types=expense_types, storages=storages)
            messages.success(request, 'Контрагент успешно отредактирован.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Partner.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/bank/partners')


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

    def post(self, request):
        card_id = request.GET.get('id')
        name = request.POST.get('name')
        storage_id = request.POST.get('storage_id')

        try:
            CardService().edit(card_id=card_id, name=name, storage_id=storage_id)
            messages.success(request, 'Карта успешно отредактирована.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Card.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/bank/cards')


class MoneyView(BaseLkView):
    template_name = 'lk/money/index.html'


@login_required
def update_money(request):
    row_id = request.GET.get('id')

    try:
        MoneyService().update(row_id=row_id)
        messages.success(request, 'Запись успешно обновлена.')
    except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Money.DoesNotExist) as error:
        messages.error(request, error)

    return redirect('/lk/money')


class MoneyEditView(ObjectEditMixin):
    template_name = 'lk/money/edit.html'
    model = Money

    def post(self, request):
        row_id = request.GET.get('id')
        sum_cash_morning = request.POST.get('sum_cash_morning')
        sum_cash_end_day = request.POST.get('sum_cash_end_day')
        barmen_percent = request.POST.get('barmen_percent')

        try:
            MoneyService().money_edit(row_id=row_id, sum_cash_morning=sum_cash_morning,
                                      sum_cash_end_day=sum_cash_end_day, barmen_percent=barmen_percent)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Money.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/money')


class TimetableView(BaseLkView):
    template_name = 'lk/timetable/index.html'


class CreateTimetableView(ObjectCreateMixin):
    model = Timetable
    template_name = 'lk/timetable/create.html'
    success_url = '/lk/timetable'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().all()
        context['positions'] = JobsService().positions_all()

        return context

    def post(self, request):
        date_at = request.POST.get('date_at')
        employee_id = request.POST.get('employee_id')
        oklad = request.POST.get('oklad')
        position_id = request.POST.get('position_id')
        storage_id = request.POST.get('storage_id')

        try:
            TimetableService().create(date_at=date_at, employee_id=employee_id,
                                      oklad=oklad, position_id=position_id, storage_id=storage_id)
            messages.success(request, 'Запись успешно создана.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/lk/timetable')


class EditTimetableView(ObjectEditMixin):
    model = Timetable
    template_name = 'lk/timetable/edit.html'
    success_url = '/lk/timetable'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().all()
        context['positions'] = JobsService().positions_all()

        return context

    def post(self, request):
        timetable_id = request.GET.get('id')
        date_at = request.POST.get('date_at')
        employee_id = request.POST.get('employee_id')
        oklad = request.POST.get('oklad')
        position_id = request.POST.get('position_id')
        storage_id = request.POST.get('storage_id')

        try:
            TimetableService().edit(timetable_id=timetable_id, date_at=date_at, employee_id=employee_id,
                                    oklad=oklad, position_id=position_id, storage_id=storage_id)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Timetable.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/timetable')


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
        date_at = request.POST.get('date_at')
        payment_receiver = request.POST.get('payment_receiver')
        expense_sum = request.POST.get('sum')
        comment = request.POST.get('comment')
        storage_id = request.POST.get('storage_id')
        type_id = request.POST.get('type_id')
        source_id = request.POST.get('source_id')

        try:
            ExpenseService().create(date_at=date_at, payment_receiver=payment_receiver, expense_sum=expense_sum,
                                    comment=comment, storage_id=storage_id,
                                    expense_type_id=type_id, expense_source_id=source_id)
            messages.success(request, 'Расход успешно создан.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/lk/expenses')


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

    def post(self, request):
        expense_id = request.GET.get('id')
        date_at = request.POST.get('date_at')
        payment_receiver = request.POST.get('payment_receiver')
        expense_sum = request.POST.get('sum')
        comment = request.POST.get('comment')
        storage_id = request.POST.get('storage_id')
        type_id = request.POST.get('type_id')
        source_id = request.POST.get('source_id')

        try:
            ExpenseService().edit(expense_id=expense_id, date_at=date_at, payment_receiver=payment_receiver,
                                  expense_sum=expense_sum,
                                  comment=comment, storage_id=storage_id,
                                  expense_type_id=type_id, expense_source_id=source_id)
            messages.success(request, 'Расход успешно отредактирован.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Expense.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/expenses')


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
        context['employees'] = EmployeeService().all()
        context['months'] = get_months()

        return context

    def post(self, request):
        date_at = request.POST.get('date_at')
        salary_type = request.POST.get('type')
        employee_id = request.POST.get('employee_id')
        storage_id = request.POST.get('storage_id')
        oklad = request.POST.get('oklad')
        percent = request.POST.get('percent')
        premium = request.POST.get('premium')
        month = request.POST.get('month')
        period = request.POST.get('period')

        try:
            SalaryService().create(date_at=date_at, salary_type=salary_type, employee_id=employee_id,
                                   storage_id=storage_id, oklad=oklad, percent=percent, premium=premium,
                                   month=month, period=period)
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/lk/salary')


class EditSalaryView(ObjectEditMixin):
    template_name = 'lk/salary/edit.html'
    model = Salary
    success_url = '/lk/salary'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().all()
        context['months'] = get_months()

        return context

    def post(self, request):
        salary_id = request.GET.get('id')
        date_at = request.POST.get('date_at')
        salary_type = request.POST.get('type')
        employee_id = request.POST.get('employee_id')
        storage_id = request.POST.get('storage_id')
        oklad = request.POST.get('oklad')
        percent = request.POST.get('percent')
        premium = request.POST.get('premium')
        month = request.POST.get('month')
        period = request.POST.get('period')

        try:
            SalaryService().edit(salary_id=salary_id, date_at=date_at, salary_type=salary_type,
                                 employee_id=employee_id, storage_id=storage_id, oklad=oklad,
                                 percent=percent, premium=premium, month=month, period=period)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Salary.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/salary')


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
        context['pays'] = CatalogService().get_catalog_by_catalog_type_name_in_list(
            [settings.PAYIN_CATEGORY, settings.PAYOUT_CATEGORY])

        return context

    def post(self, request):
        date_at = request.POST.get('date_at')
        storage_id = request.POST.get('storage_id')
        pay_type = request.POST.get('type')
        pay_sum = request.POST.get('sum')
        comment = request.POST.get('comment')
        from_to_id = request.POST.get('from_to_id')

        try:
            PaysService().create(date_at=date_at, storage_id=storage_id,
                                 pay_type=pay_type, pay_sum=pay_sum, comment=comment,
                                 from_to_id=from_to_id)
            messages.success(request, 'Запись успешно создана.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/lk/pays')


class EditPaysView(ObjectEditMixin):
    template_name = 'lk/pays/edit.html'
    model = Pays
    success_url = '/lk/pays'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['pays'] = CatalogService().get_catalog_by_catalog_type_name_in_list(
            [settings.PAYIN_CATEGORY, settings.PAYOUT_CATEGORY])

        return context

    def post(self, request):
        pay_id = request.GET.get('id')
        date_at = request.POST.get('date_at')
        storage_id = request.POST.get('storage_id')
        pay_type = request.POST.get('type')
        pay_sum = request.POST.get('sum')
        comment = request.POST.get('comment')
        from_to_id = request.POST.get('from_to_id')

        try:
            PaysService().edit(pay_id=pay_id, date_at=date_at, storage_id=storage_id,
                               pay_type=pay_type, pay_sum=pay_sum, comment=comment,
                               from_to_id=from_to_id)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Pays.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/pays')


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
        context['employees'] = EmployeeService().all()
        context['reasons'] = CatalogService().get_catalog_by_catalog_type_name_contains(settings.FINE_REASON_CATEGORY)

        return context

    def post(self, request):
        date_at = request.POST.get('date_at')
        employee_id = request.POST.get('employee_id')
        fine_sum = request.POST.get('sum')
        reason_id = request.POST.get('reason_id')

        try:
            FineService().create(date_at=date_at, employee_id=employee_id,
                                 fine_sum=fine_sum, reason_id=reason_id)
            messages.success(request, 'Запись успешно создана.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect('/lk/fines')


class EditFinesView(ObjectEditMixin):
    template_name = 'lk/fines/edit.html'
    model = Fine
    success_url = '/lk/fines'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['employees'] = EmployeeService().all()
        context['reasons'] = CatalogService().get_catalog_by_type(settings.FINE_REASON_CATEGORY)

        return context

    def post(self, request):
        fine_id = request.GET.get('id')
        date_at = request.POST.get('date_at')
        employee_id = request.POST.get('employee_id')
        fine_sum = request.POST.get('sum')
        reason_id = request.POST.get('reason_id')

        try:
            FineService().edit(fine_id=fine_id, date_at=date_at, employee_id=employee_id,
                               fine_sum=fine_sum, reason_id=reason_id)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Fine.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/fines')


class DeleteFineView(ObjectDeleteMixin):
    model = Fine
    success_url = '/lk/fines'

    def get(self, request):
        FineService().delete(fine_id=request.GET.get('id'))
        messages.success(request, 'Штраф успешно удален.')
        return redirect('/lk/fines')


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
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        birth_date = request.POST.get('birth-date')
        address = request.POST.get('address')
        job_id = request.POST.get('job-id')
        storage_id = request.POST.get('storage-id')
        phone = request.POST.get('phone')
        status = request.POST.get('status')
        photo = request.FILES.get('employee_photo')

        try:
            EmployeeService().employee_create(request, first_name=first_name, last_name=last_name,
                                              birth_date=birth_date,
                                              address=address, job_id=job_id, storage_id=storage_id, phone=phone,
                                              status=status, photo=photo)
            messages.success(request, 'Сотрудник успешно создан.')
            url = '/lk/employees'
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, exceptions.UniqueFieldError,
                exceptions.IncorrectFieldError) as error:
            messages.error(request, error)
            url = '/lk/employees/create'

        return redirect(url)


class EditEmployeeView(ObjectEditMixin):
    template_name = 'lk/employees/edit.html'
    model = Employee
    success_url = '/lk/employees'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['storages'] = StorageService().storages_all()
        context['jobs'] = JobsService().jobs_all()

        return context

    def post(self, request):
        employee_id = request.GET.get('id')
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        birth_date = request.POST.get('birth_date')
        address = request.POST.get('address')
        job_place_id = request.POST.get('job_place_id')
        storage_id = request.POST.get('storage_id')
        phone = request.POST.get('phone')
        status = request.POST.get('status')
        photo = request.FILES.get('employee_photo')

        try:
            EmployeeService().employee_edit(employee_id=employee_id, first_name=first_name, last_name=last_name,
                                            birth_date=birth_date, address=address, job_place_id=job_place_id,
                                            storage_id=storage_id, phone=phone, status=status, photo=photo)
            messages.success(request, 'Сотрудник успешно отредактирован.')
            url = '/lk/employees'
        except (exceptions.FieldCannotBeEmptyError, exceptions.FieldNotFoundError, exceptions.UniqueFieldError,
                exceptions.IncorrectFieldError) as error:
            messages.error(request, error)
            url = f'/lk/employees/edit?id={employee_id}'

        return redirect(url)


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
        context['products'] = Product.objects.filter(
            category__name__in=[settings.TOVAR_BEER_CATEGORY, settings.TOVAR_DRINKS_CATEGORY])
        context['suppliers'] = Supplier.objects.all()
        context['payment_types'] = Catalog.objects.filter(catalog_types__name=settings.EXPENSE_SOURCE_CATEGORY)

        return context

    def post(self, request):
        pass


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

    def post(self, request):
        pass


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


class TimetableUpdateView(BaseLkView):

    def get(self, request):
        calculate_percent_premium_for_all.delay()
        return HttpResponse('update started')


class ItemDeficitView(BaseLkView):
    template_name = 'lk/need_items.html'


class ItemDeficitSendView(BaseLkView):

    def get(self, request):
        context = self.get_context_data(request)

        request_id = request.GET.get('id')

        try:
            receive_status = ItemDeficitService().send(request_id=request_id, user=context.get('profile'))
            if receive_status:
                messages.success(request, 'Статус успешно обновлен.')
            else:
                messages.error(request, 'Этот запрос уже обработан.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, ItemDeficit.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/need_items')


class BarActionsView(BaseLkView):
    template_name = 'lk/bar_actions.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "settings": Setting.objects.all()
        })

        return context


def send_message_on_bar(request):
    storage = request.POST.get('storage_id')
    message = request.POST.get('message')

    try:
        BarActionsService().send_message_on_bar(storage=storage, message=message)
        messages.success(request, 'Сообщение успешно отправлено.')
    except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
        messages.error(request, error)

    return redirect('/lk/bars/actions')


class MalfunctionsView(BaseLkView):
    template_name = 'lk/malfunctions.html'


class MalfunctionDeleteView(ObjectDeleteMixin):
    model = Malfunction
    success_url = '/lk/malfunctions'
