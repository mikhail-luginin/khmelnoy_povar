from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

from core.logs import LogsService
from core.services.reports_service import ReportsService
from core.utils.time import get_months, get_current_time
from core.mixins import BaseLkView, ObjectEditMixin, ObjectCreateMixin, ObjectDeleteMixin
from core import exceptions
from core.services import salary_service, bar_service, item_deficit_service, reviews_service, catalog_service, \
                          positions_service, money_service, employees_service, expenses_service, pays_service, \
                          timetable_service, storage_service, statement_service, salary_crud, product_remains_service, \
                          supplier_service, fines_service, product_service

from .tasks import calculate_percent_premium_for_all, update_all_money
from .services import index_page

from apps.bar.services.malfunctions import MalfunctionService
from apps.repairer.services import RepairerService
from apps.purchaser.services import PurchaserService

from apps.lk.models import Catalog, CatalogType, Card, Expense, Fine, Employee, ItemDeficit, Partner
from apps.bar.models import Position, Timetable, Money, Salary, Pays, Arrival, TovarRequest, Setting
from apps.repairer.models import Malfunction


class IndexView(BaseLkView):
    template_name = 'lk/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "employees_data": index_page.employees_by_storages()
        })

        return context


class CatalogView(BaseLkView):
    template_name = 'lk/catalog/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "catalog_types": catalog_service.get_catalog_types()
        })

        return context


class CatalogCreateView(BaseLkView):

    def post(self, request):
        try:
            catalog_service.catalog_create(name=request.POST.get('catalog-name'), linked=request.POST.getlist('linked'))
            messages.success(request, 'Запись успешно добавлена в справочник.')
        except (exceptions.FieldNotFoundError, CatalogType.DoesNotExist) as error:
            messages.error(request, str(error))

        return redirect('/lk/catalog')


class CatalogTypeCreateView(BaseLkView):

    def post(self, request):
        try:
            catalog_service.catalog_type_create(name=request.POST.get('name'))
            messages.success(request, 'Тип каталога успешно создан.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

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
        context.update({
            "types": catalog_service.get_catalog_types(),
            "linked_types": catalog_service.get_catalog_linked_types(catalog_id=request.GET.get('id'))
        })

        return context

    def post(self, request):
        try:
            catalog_service.catalog_edit(row_id=request.GET.get('id'), name=request.POST.get('name'),
                                         linked=request.POST.getlist('linked'))
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, CatalogType.DoesNotExist) as error:
            messages.error(request, str(error))

        return redirect('/lk/catalog')


class CatalogTypeEditView(ObjectEditMixin):
    model = CatalogType
    template_name = 'lk/catalog/type_edit.html'

    def post(self, request):
        try:
            catalog_service.catalog_type_edit(row_id=request.GET.get('id'), name=request.POST.get('name'))
            messages.success(request, 'Тип справочника успешно отредактирован.')
        except (exceptions.FieldNotFoundError, CatalogType.DoesNotExist) as error:
            messages.error(request, str(error))

        return redirect('/lk/catalog')


class BarsView(BaseLkView):
    template_name = 'lk/bars.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "bars": bar_service.bar_settings()
        })

        return context


class BarSettingsView(BaseLkView):
    template_name = 'lk/bars_settings.html'

    def get_context_data(self, request, **kwargs) -> dict:
        storage_id = request.GET.get('id')

        context = super().get_context_data(request, **kwargs)
        context.update({
            "questions": bar_service.questions_for_link(),
            "row": bar_service.get_setting_by_storage_id(storage_id=storage_id),
            "products": product_service.nomenclature_by_category(category_name=settings.TOVAR_WARE_CATEGORY),
            "remains": product_remains_service.remains_by_storage_id(storage_id=storage_id)
        })

        return context

    def post(self, request):
        try:
            bar_service.settings_edit(storage_id=request.GET.get('id'), percent=request.POST.get('percent'),
                                      tg_chat_id=request.POST.get('chat-id'))
            messages.success(request, 'Настройки бара успешно обновлены')
        except (exceptions.FieldNotFoundError, Setting.DoesNotExist) as error:
            messages.error(request, str(error))

        return redirect('/lk/bars')


class PositionsView(BaseLkView):
    template_name = 'lk/positions/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "jobs": positions_service.jobs_all()
        })

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
            positions_service.position_create(position_oklad=position_oklad, position_is_usil=position_is_usil,
                                              position_name=position_name, position_is_trainee=position_is_trainee,
                                              position_is_called=position_is_called,
                                              position_all_storages=position_all_storages,
                                              position_has_percent=position_has_percent,
                                              position_has_premium=position_has_premium,
                                              position_job_ids=position_job_ids, priority_id=priority_id)
            messages.success(request, 'Позиция успешно создана.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

        return redirect('/lk/positions')


class PositionsEditView(ObjectEditMixin):
    template_name = 'lk/positions/edit.html'
    model = Position

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "jobs": positions_service.jobs_all()
        })

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
            positions_service.position_edit(position_id=position_id, position_name=position_name,
                                            position_is_trainee=position_is_trainee, position_is_called=position_is_called,
                                            position_job_ids=position_job_ids, position_is_usil=position_is_usil,
                                            position_has_premium=position_has_premium,
                                            position_has_percent=position_has_percent,
                                            position_all_storages=position_all_storages, position_oklad=position_oklad,
                                            priority_id=priority_id)
            messages.success(request, 'Позиция успешно отредактирована')
        except (exceptions.FieldNotFoundError, Position.DoesNotExist) as error:
            messages.error(request, str(error))

        return redirect('/lk/positions')


class PositionDeleteView(ObjectDeleteMixin):
    model = Position
    success_url = '/lk/positions'


class JobAddView(BaseLkView):

    def post(self, request):
        job_name = request.POST.get('job-name')
        job_gain_oklad_accrual = request.POST.get('job-gain-oklad-accrual')
        job_main_oklad_accrual = request.POST.get('job-main-oklad-accrual')
        job_gain_oklad_receiving = request.POST.get('job-gain-oklad-receiving')
        job_main_oklad_receiving = request.POST.get('job-main-oklad-receiving')

        try:
            positions_service.job_create(job_name=job_name,
                                         job_gain_oklad_accrual=job_gain_oklad_accrual,
                                         job_main_oklad_accrual=job_main_oklad_accrual,
                                         job_main_oklad_receiving=job_main_oklad_receiving,
                                         job_gain_oklad_receiving=job_gain_oklad_receiving)
            messages.success(request, 'Должность успешно создана.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

        return redirect('/lk/positions')


class BankView(BaseLkView):
    template_name = 'lk/bank.html'


@login_required
def bank_update(request):
    return statement_service.StatementUpdateService().update(request)


class BankPartnersView(BaseLkView):
    template_name = 'lk/partners/index.html'


class BankPartnerEditView(ObjectEditMixin):
    template_name = 'lk/partners/edit.html'
    model = Partner

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "types": catalog_service.get_catalog_by_type(type_name=settings.EXPENSE_TYPE_CATEGORY),
            "storages": storage_service.storages_all()
        })

        return context

    def post(self, request):
        partner_id = request.GET.get('id')
        friendly_name = request.POST.get('friendly_name')
        expense_types = request.POST.getlist('expense_types')
        storages = request.POST.getlist('storages')

        try:
            statement_service.PartnerService().edit(partner_id=partner_id, friendly_name=friendly_name,
                                                    expense_types=expense_types, storages=storages)
            messages.success(request, 'Контрагент успешно отредактирован.')
        except (exceptions.FieldNotFoundError, Partner.DoesNotExist) as error:
            messages.error(request, str(error))

        return redirect('/lk/bank/partners')


class BankCardsView(BaseLkView):
    template_name = 'lk/cards/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "undefined_cards": statement_service.CardService().get_undefined_cards(),
            "cards": statement_service.CardService().cards_all()
        })

        return context


class BankCardCreateView(ObjectCreateMixin):
    template_name = 'lk/cards/create.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "current_card": request.GET.get('card'),
            "storages": storage_service.storages_all()
        })

        return context

    def post(self, request):
        return statement_service.CardService().card_create(request)


class BankCardEditView(ObjectEditMixin):
    template_name = 'lk/cards/edit.html'
    model = Card
    success_url = '/lk/bank/cards'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all()
        })

        return context

    def post(self, request):
        card_id = request.GET.get('id')
        name = request.POST.get('name')
        storage_id = request.POST.get('storage_id')

        try:
            statement_service.CardService().edit(card_id=card_id, name=name, storage_id=storage_id)
            messages.success(request, 'Карта успешно отредактирована.')
        except (exceptions.FieldNotFoundError, Card.DoesNotExist) as error:
            messages.error(request, str(error))

        return redirect('/lk/bank/cards')


class MoneyView(BaseLkView):
    template_name = 'lk/money/index.html'


@login_required
def update_all_money_and_sessions(request):
    update_all_money.delay()
    messages.success(request, 'Кассовые смены успешно обновлены.')
    return redirect('/lk/money')


@login_required
def update_money(request):
    row_id = request.GET.get('id')

    try:
        money_service.update(row_id=row_id)
        messages.success(request, 'Запись успешно обновлена.')
    except (exceptions.FieldNotFoundError, Money.DoesNotExist) as error:
        messages.error(request, str(error))

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
            money_service.money_edit(row_id=row_id, sum_cash_morning=sum_cash_morning,
                                     sum_cash_end_day=sum_cash_end_day, barmen_percent=barmen_percent)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, Money.DoesNotExist) as error:
            messages.error(request, str(error))

        return redirect('/lk/money')


class TimetableView(BaseLkView):
    template_name = 'lk/timetable/index.html'


class CreateTimetableView(ObjectCreateMixin):
    model = Timetable
    template_name = 'lk/timetable/create.html'
    success_url = '/lk/timetable'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "employees": employees_service.employees_all(),
            "positions": positions_service.positions_all()
        })

        return context

    def post(self, request):
        date_at = request.POST.get('date_at')
        employee_id = request.POST.get('employee_id')
        oklad = request.POST.get('oklad')
        position_id = request.POST.get('position_id')
        storage_id = request.POST.get('storage_id')

        try:
            timetable_service.create(date_at=date_at, employee_id=employee_id,
                                     oklad=oklad, position_id=position_id, storage_id=storage_id)
            messages.success(request, 'Запись успешно создана.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

        return redirect('/lk/timetable')


class EditTimetableView(ObjectEditMixin):
    model = Timetable
    template_name = 'lk/timetable/edit.html'
    success_url = '/lk/timetable'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "employees": employees_service.employees_all(),
            "positions": positions_service.positions_all()
        })

        return context

    def post(self, request):
        timetable_id = request.GET.get('id')
        date_at = request.POST.get('date_at')
        employee_id = request.POST.get('employee_id')
        oklad = request.POST.get('oklad')
        position_id = request.POST.get('position_id')
        storage_id = request.POST.get('storage_id')

        try:
            timetable_service.edit(timetable_id=timetable_id, date_at=date_at, employee_id=employee_id,
                                   oklad=oklad, position_id=position_id, storage_id=storage_id)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, Timetable.DoesNotExist) as error:
            messages.error(request, str(error))

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
        context.update({
            "storages": storage_service.storages_all(),
            "types": catalog_service.get_catalog_by_catalog_type_name_contains(name='расходы'),
            "sources": catalog_service.get_catalog_by_type(type_name=settings.EXPENSE_SOURCE_CATEGORY)
        })

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
            expenses_service.create(date_at=date_at, payment_receiver=payment_receiver, expense_sum=expense_sum,
                                    comment=comment, storage_id=storage_id,
                                    expense_type_id=type_id, expense_source_id=source_id)
            messages.success(request, 'Расход успешно создан.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

        return redirect('/lk/expenses')


class EditExpenseView(ObjectEditMixin):
    template_name = 'lk/expenses/edit.html'
    model = Expense
    success_url = '/lk/expenses'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "types": catalog_service.get_catalog_by_catalog_type_name_contains(name='расходы'),
            "sources": catalog_service.get_catalog_by_type(type_name=settings.EXPENSE_SOURCE_CATEGORY)
        })

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
            expenses_service.edit(expense_id=expense_id, date_at=date_at, payment_receiver=payment_receiver,
                                  expense_sum=expense_sum,
                                  comment=comment, storage_id=storage_id,
                                  expense_type_id=type_id, expense_source_id=source_id)
            messages.success(request, 'Расход успешно отредактирован.')
        except (exceptions.FieldNotFoundError, Expense.DoesNotExist) as error:
            messages.error(request, str(error))

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
        context.update({
            "storages": storage_service.storages_all(),
            "employees": employees_service.employees_all(),
            "months": get_months()
        })

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
            salary_crud.create(date_at=date_at, salary_type=salary_type, employee_id=employee_id,
                               storage_id=storage_id, oklad=oklad, percent=percent, premium=premium,
                               month=month, period=period)
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

        return redirect('/lk/salary')


class EditSalaryView(ObjectEditMixin):
    template_name = 'lk/salary/edit.html'
    model = Salary
    success_url = '/lk/salary'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "employees": employees_service.employees_all(),
            "months": get_months()
        })

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
            salary_crud.edit(salary_id=salary_id, date_at=date_at, salary_type=salary_type,
                             employee_id=employee_id, storage_id=storage_id, oklad=oklad,
                             percent=percent, premium=premium, month=month, period=period)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, Salary.DoesNotExist) as error:
            messages.error(request, str(error))

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
        context.update({
            "storages": storage_service.storages_all(),
            "pays": catalog_service.get_catalog_by_catalog_type_name_in_list(names=[settings.PAYIN_CATEGORY,
                                                                                    settings.PAYOUT_CATEGORY])
        })

        return context

    def post(self, request):
        date_at = request.POST.get('date_at')
        storage_id = request.POST.get('storage_id')
        pay_type = request.POST.get('type')
        pay_sum = request.POST.get('sum')
        comment = request.POST.get('comment')
        from_to_id = request.POST.get('from_to_id')

        try:
            pays_service.create(date_at=date_at, storage_id=storage_id,
                                pay_type=pay_type, pay_sum=pay_sum, comment=comment,
                                from_to_id=from_to_id)
            messages.success(request, 'Запись успешно создана.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

        return redirect('/lk/pays')


class EditPaysView(ObjectEditMixin):
    template_name = 'lk/pays/edit.html'
    model = Pays
    success_url = '/lk/pays'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "pays": catalog_service.get_catalog_by_catalog_type_name_in_list(names=[settings.PAYIN_CATEGORY,
                                                                                    settings.PAYOUT_CATEGORY])
        })

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
            pays_service.edit(pay_id=pay_id, date_at=date_at, storage_id=storage_id,
                              pay_type=pay_type, pay_sum=pay_sum, comment=comment,
                              from_to_id=from_to_id)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, Pays.DoesNotExist) as error:
            messages.error(request, str(error))

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
        context.update({
            "storages": storage_service.storages_all(),
            "employees": employees_service.employees_all(),
            "reasons": catalog_service.get_catalog_by_catalog_type_name_contains(settings.FINE_REASON_CATEGORY)
        })

        return context

    def post(self, request):
        date_at = request.POST.get('date_at')
        employee_id = request.POST.get('employee_id')
        fine_sum = request.POST.get('sum')
        reason_id = request.POST.get('reason_id')

        try:
            fines_service.create(date_at=date_at, employee_id=employee_id,
                                 fine_sum=fine_sum, reason_id=reason_id)
            messages.success(request, 'Запись успешно создана.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

        return redirect('/lk/fines')


class EditFinesView(ObjectEditMixin):
    template_name = 'lk/fines/edit.html'
    model = Fine
    success_url = '/lk/fines'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "employees": employees_service.employees_all(),
            "reasons": catalog_service.get_catalog_by_catalog_type_name_contains(settings.FINE_REASON_CATEGORY)
        })

        return context

    def post(self, request):
        fine_id = request.GET.get('id')
        date_at = request.POST.get('date_at')
        employee_id = request.POST.get('employee_id')
        fine_sum = request.POST.get('sum')
        reason_id = request.POST.get('reason_id')

        try:
            fines_service.edit(fine_id=fine_id, date_at=date_at, employee_id=employee_id,
                               fine_sum=fine_sum, reason_id=reason_id)
            messages.success(request, 'Запись успешно отредактирована.')
        except (exceptions.FieldNotFoundError, Fine.DoesNotExist) as error:
            messages.error(request, str(error))

        return redirect('/lk/fines')


class DeleteFineView(ObjectDeleteMixin):
    model = Fine
    success_url = '/lk/fines'

    def get(self, request):
        fines_service.delete(fine_id=request.GET.get('id'))
        messages.success(request, 'Штраф успешно удален.')
        return redirect('/lk/fines')


class EmployeesView(BaseLkView):
    template_name = 'lk/employees/index.html'


class CreateEmployeeView(ObjectCreateMixin):
    template_name = 'lk/employees/create.html'
    model = Employee

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "jobs": positions_service.jobs_all()
        })

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
        description = request.POST.get('description')

        try:
            employees_service.employee_create(request, first_name=first_name, last_name=last_name,
                                              birth_date=birth_date,
                                              address=address, job_id=job_id, storage_id=storage_id, phone=phone,
                                              status=status, photo=photo, description=description)
            messages.success(request, 'Сотрудник успешно создан.')
            url = '/lk/employees'
        except (exceptions.FieldNotFoundError, exceptions.UniqueFieldError, exceptions.IncorrectFieldError) as error:
            messages.error(request, str(error))
            url = '/lk/employees/create'

        return redirect(url)


class EditEmployeeView(ObjectEditMixin):
    template_name = 'lk/employees/edit.html'
    model = Employee
    success_url = '/lk/employees'

    def get_context_data(self, request, **kwargs) -> dict:
        employee_id = request.GET.get('id')

        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "jobs": positions_service.jobs_all(),
            "salaries": salary_service.SalaryService().get_money_data_employee(request).get('entire_salary_data'),
            "last_work_day": employees_service.last_work_day(employee_id=employee_id),
            "employee_logs": employees_service.employee_logs(employee_id=employee_id)
        })

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
        description = request.POST.get('description')
        status_change_comment = request.POST.get('status_change_comment')

        try:
            employees_service.employee_edit(employee_id=employee_id, first_name=first_name, last_name=last_name,
                                            birth_date=birth_date, address=address, job_place_id=job_place_id,
                                            storage_id=storage_id, phone=phone, status=status, photo=photo,
                                            description=description, status_change_comment=status_change_comment)
            messages.success(request, 'Сотрудник успешно отредактирован.')
            url = '/lk/employees'
        except (exceptions.FieldNotFoundError, exceptions.UniqueFieldError, exceptions.IncorrectFieldError) as error:
            messages.error(request, str(error))
            url = f'/lk/employees/edit?id={employee_id}'

        return redirect(url)


class DissmissEmployeeView(BaseLkView):

    def get(self, request):
        return employees_service.dismiss(request)


class ReturnToWorkEmployeeView(BaseLkView):

    def get(self, request):
        return employees_service.return_to_work(request)


class ArrivalsView(BaseLkView):
    template_name = 'lk/arrivals/index.html'


class ArrivalCreateView(ObjectCreateMixin):
    template_name = 'lk/arrivals/create.html'
    model = Arrival
    success_url = '/lk/tovar/arrivals'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "products": product_service.nomenclature_by_categories(categories=[settings.TOVAR_BEER_CATEGORY,
                                                                               settings.TOVAR_DRINKS_CATEGORY]),
            "suppliers": supplier_service.suppliers_all(),
            "payment_types": catalog_service.get_catalog_by_type(type_name=settings.EXPENSE_SOURCE_CATEGORY)
        })

        return context

    def post(self, request):
        pass


class ArrivalEditView(ObjectEditMixin):
    template_name = 'lk/arrivals/edit.html'
    model = Arrival
    success_url = '/lk/tovar/arrivals'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all(),
            "products": product_service.nomenclature_by_categories(categories=[settings.TOVAR_BEER_CATEGORY,
                                                                               settings.TOVAR_DRINKS_CATEGORY]),
            "suppliers": supplier_service.suppliers_all(),
            "payment_types": catalog_service.get_catalog_by_type(type_name=settings.EXPENSE_SOURCE_CATEGORY)
        })

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
    template_name = 'lk/need_items/index.html'


class ItemDeficitSendView(BaseLkView):

    def post(self, request):
        context = self.get_context_data(request)

        request_id = request.GET.get('id')

        try:
            receive_status = item_deficit_service.send(request_id=request_id, user=context.get('profile'),
                                                       sended_amount=request.POST.get('sended_amount'),
                                                       comment=request.POST.get('comment'))
            if receive_status:
                messages.success(request, 'Статус успешно обновлен.')
            else:
                messages.error(request, 'Этот запрос уже обработан.')
        except (exceptions.FieldNotFoundError, ItemDeficit.DoesNotExist) as error:
            messages.error(request, str(error))

        url = request.META.get('HTTP_REFERER')
        return redirect(url if url else '/lk/item_deficit')


class BarActionsView(BaseLkView):
    template_name = 'lk/bar_actions.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "settings": bar_service.bar_settings()
        })

        return context


class SendMessageOnBar(BaseLkView):
    
    def post(self, request):
        context = self.get_context_data(request)
        
        storages = request.POST.getlist('storages')
        message = request.POST.get('message')

        try:
            profile = context.get('profile')
            bar_service.send_message_on_bar(storages=storages, message=message, profile=profile)
            messages.success(request, 'Сообщение успешно отправлено.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

        url = request.META.get('HTTP_REFERER')
        return redirect(url if url else '/lk/bars/actions')


class MalfunctionsView(BaseLkView):
    template_name = 'lk/malfunctions/index.html'


class MalfunctionDeleteView(ObjectDeleteMixin):
    model = Malfunction
    success_url = '/lk/malfunctions'


class MalfunctionCompleteView(BaseLkView):

    def get(self, request):
        malfunction_id = request.GET.get('id')

        try:
            RepairerService().malfunction_repaired(malfunction_id=malfunction_id)
            messages.success(request, 'Ваш ответ был успешно отправлен.')
        except (exceptions.FieldNotFoundError, Malfunction.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/lk/malfunctions')


@login_required
def link_question_to_bar_setting(request):
    question_text = request.POST.get('question_text')
    question_id = request.GET.get('question_id')
    storage_id = request.GET.get('id')

    try:
        bar_service.link_question_to_storage(question_text=question_text, storage_id=storage_id,
                                                          question_id=question_id)
        messages.success(request, 'Вопрос для конца дня успешно привязан к заведению.')
    except (exceptions.FieldNotFoundError, Setting.DoesNotExist) as error:
        messages.error(request, str(error))

    return redirect('/lk/bars/settings?id=' + storage_id)


class ReviewsView(BaseLkView):
    template_name = 'lk/reviews/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "jobs": positions_service.jobs_all(),
            "storages": storage_service.storages_all()
        })
        return context


@login_required
def review_create(request):
    if request.method == "POST":
        photo = request.FILES.get('review_photo')
        review_date = request.POST.get('review_date')
        storage_id = request.POST.get('storage_id')
        jobs = request.POST.getlist('jobs')

        try:
            reviews_service.create(photo=photo, review_date=review_date, storage_id=storage_id, jobs=jobs)
            messages.success(request, 'Отзыв успешно добавлен.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, str(error))

        return redirect('/lk/reviews')
    

@login_required
def review_link_to_employee(request):
    if request.method == "GET":
        review_id = request.GET.get('id')
        
        try:
            reviews_service.link_to_employee(review_id=review_id)
            messages.success(request, 'Отзыв привязан к сотрудникам.')
        except Exception as error:
            messages.error(request, str(error))
            
        return redirect('/lk/reviews')


class MalfunctionCreateView(ObjectCreateMixin):
    template_name = 'lk/malfunctions/create.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all()
        })

        return context

    def post(self, request):
        photo = request.FILES.get('malfunction-photo')
        fault_object = request.POST.get('fault-object')
        description = request.POST.get('malfunction-description')
        storage_id = request.POST.get('storage_id')

        try:
            MalfunctionService().malfunction_create(storage_id=storage_id, photo=photo,
                                                    fault_object=fault_object, description=description)
            messages.success(request, 'Неисправность успешно занесена в список.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, error)

        return redirect('/lk/malfunctions')


class NeedItemsCreateView(ObjectCreateMixin):
    template_name = 'lk/need_items/create.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "storages": storage_service.storages_all()
        })

        return context

    def post(self, request):
        item = request.POST.get('need_item')
        amount = request.POST.get('amount_need_item')
        storage_id = request.POST.get('storage_id')

        try:
            item_deficit_service.create(storage_id=storage_id, item=item, amount=amount)
            messages.success(request, 'Заявка на нехватку успешно создана.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, error)

        return redirect('/lk/need_items')


class LogsView(BaseLkView):
    template_name = 'lk/logs.html'


def update_logs_view(request):
    if request.method == 'GET':
        data = LogsService().update(timestamp=request.GET.get('timestamp'))

        return JsonResponse({"data": data}, status=200, safe=False)


class LogsWithFilterView(BaseLkView):
    template_name = 'lk/logs_with_filter.html'


class MoneyDifferencesView(BaseLkView):
    template_name = 'lk/money/differences.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "rows": money_service.rows_with_difference()
        })

        return context


class ExpenseStatusView(BaseLkView):

    def get(self, request):
        expense_id = request.GET.get('id')
        status = request.GET.get('status')
        comment = request.GET.get('comment')

        try:
            expenses_service.change_status(expense_id=expense_id, status=status, comment=comment)
            messages.success(request, 'Статус записи успешно обновлен.')
        except exceptions.FieldNotFoundError as error:
            messages.error(request, str(error))

        return redirect('/lk/expenses')


class PurchaserView(BaseLkView):
    template_name = 'lk/purchaser/index.html'


@login_required
def get_table_for_purchaser(request):
    return JsonResponse({'data': PurchaserService().get_info_for_purchaser_difference()})


@login_required
def product_remains_add(request):
    storage_id = request.GET.get('id')

    remains = {}
    for key, value in request.POST.items():
        if key != 'csrfmiddlewaretoken':
            if value != '':
                remains.update({key: value})
    product_remains_service.add_remain(remains=remains, storage_id=storage_id)

    messages.success(request, 'Остатки успешно занесены.')
    return redirect(f'/lk/bars/settings?id={storage_id}')


class ReportsView(BaseLkView):
    template_name = 'lk/reports/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "months": get_months(),
            "storages": storage_service.storages_all()
        })

        return context


class ReportsMoneyUpdateView(BaseLkView):

    def get(self, request):
        data = ReportsService().update_money_reports()
        return JsonResponse({"data": data}, status=200, safe=False)


class ReportExpenseTypesByStorageView(BaseLkView):
    template_name = 'lk/reports/expense_types_by_storage.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "months": get_months()
        })

        return context

    def post(self, request):
        month = request.POST.get('month')

        data = ReportsService().update_expense_types_by_storages_reports(
            year=get_current_time().year, month_id=int(month) if month else get_current_time().month
        )
        return JsonResponse({"data": data}, status=200)
