#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import redirect

from apps.bar.models import Timetable, TovarRequest, Arrival, Pays, Salary, Money, Setting
from apps.iiko.models import Storage
from apps.lk.models import Expense, Fine, ItemDeficit
from apps.repairer.models import Malfunction
from apps.repairer.services import RepairerService
from core import exceptions
from core.services import bar_service, arrival_service
from core.services import catalog_service, item_deficit_service, storage_service
from core.services.salary_service import SalaryService
from core.utils.telegram import send_message_to_telegram
from core.utils.time import today_date, get_months, get_current_time
from .exceptions import EmployeeAlreadyWorkingToday
from .services.bar_info import get_full_information_of_day, get_bar_settings, get_full_information_of_day_for_data_logs
from .services.end_day import complete_day
from .services.expenses import ExpensesPageService
from .services.fines import get_fines_on_storage_by_month
from .services.index import HomePageService
from .services.malfunctions import MalfunctionService
from .utils import BaseView, ObjectDeleteMixin, TovarRequestMixin, ArrivalMixin, InventoryMixin, DataLogsMixin


class IndexView(BaseView):
    template_name = 'bar/index.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = HomePageService().get_timetable_today(context['bar'])
        context['positions'] = HomePageService().positions_on_storage()
        context['morning_cashbox'] = HomePageService().morning_cashbox_today(context['bar'])

        return context

    def post(self, request):
        try:
            HomePageService().timetable_add(request)
            messages.success(request, 'Данные смены успешно обновлены.')
        except (EmployeeAlreadyWorkingToday, Setting.DoesNotExist) as error:
            messages.error(request, error)
        return redirect('/bar?code=' + request.GET.get('code'))


class TimetableDeleteView(ObjectDeleteMixin):
    model = Timetable


class ExpensesView(BaseView):
    template_name = 'bar/expenses.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = ExpensesPageService().get_expenses_today(context['bar'])
        context['expenses_types'] = catalog_service.get_catalog_by_type(settings.EXPENSE_TYPE_CATEGORY)
        context['expenses_sources'] = catalog_service.get_catalog_by_type(settings.EXPENSE_SOURCE_CATEGORY)
        context['timetable'] = HomePageService().get_timetable_today(context['bar'])
        context['expenses'] = ExpensesPageService().get_sum_expenses_today(context['bar'])
        context['payin_types'] = catalog_service.get_catalog_by_type(settings.PAYIN_CATEGORY)
        context['payout_types'] = catalog_service.get_catalog_by_type(settings.PAYOUT_CATEGORY)
        context['pays_rows'] = Pays.objects.filter(date_at=today_date(), storage=context['bar'])
        context['bar_setting'] = get_bar_settings(storage_id=context.get('bar').id)

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
        context['salaries'] = Salary.objects.filter(storage=context['bar'], date_at=today_date(), type=1).annotate(
            total_sum=Sum('oklad') + Sum('percent') + Sum('premium')
        )

        return context

    def post(self, request):
        return SalaryService().accrue_salary_prepayment(request)


class SalaryAccruedRowsView(BaseView):

    def get(self, request):
        storage_id = request.GET.get('storage_id')
        rows = SalaryService().salary_prepayment_rows(storage_id=storage_id)
        if rows:
            return JsonResponse({"rows": rows}, status=200, safe=False)


class SalaryForRetiredEmployeesView(BaseView):
    template_name = 'bar/salary/retired_employees.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['data'] = SalaryService().get_retired_employee_salary(context['bar'])

        return context


def salary_for_retired_employee_accrue_view(request):
    return SalaryService().accrue_retired_employee_salary(request)


class EndDayView(BaseView):
    template_name = 'bar/end_day.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['information'] = get_full_information_of_day(today_date(), context['bar'])
        context['data'] = bar_service.get_question_on_end_day_by_storage_id(storage_id=context['bar'].id)

        return context

    def post(self, request):
        return complete_day(request)


class TovarRequestBeerView(TovarRequestMixin):
    category = 'Пиво разливное.Меню'


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
    template_name = 'bar/arrival_beer.html'

    def post(self, request):
        context = self.get_context_data(request)

        post_data = request.POST.copy()
        post_data['storage_id'] = context['bar'].id
        post_data['kegs'] = True

        try:
            arrival_service.ArrivalService().invoice_drinks_create(data=post_data)
            messages.success(request, 'Накладная успешно заполнена.')
        except exceptions.FieldCannotBeEmptyError as error:
            messages.error(request, str(error))

        return redirect(f'/bar/arrivals/beer?code={request.GET.get("code")}')


class ArrivalDrinkView(ArrivalMixin):
    category = settings.TOVAR_DRINKS_CATEGORY
    template_name = 'bar/arrival_drinks.html'

    def post(self, request):
        context = self.get_context_data(request)

        post_data = request.POST.copy()
        post_data['storage_id'] = context['bar'].id
        post_data['kegs'] = False

        try:
            arrival_service.ArrivalService().invoice_drinks_create(data=post_data)
            messages.success(request, 'Накладная успешно заполнена.')
        except exceptions.FieldCannotBeEmptyError as error:
            messages.error(request, str(error))

        return redirect(f'/bar/arrivals/drinks?code={request.GET.get("code")}')


class ArrivalDeleteView(ObjectDeleteMixin):
    model = Arrival


class SalaryCalculationView(BaseView):
    template_name = 'bar/salary/calculation.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['data'] = SalaryService().get_salary_calculation_rows(context['bar'])
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
        storage_id = storage_service.storage_get(code=request.GET.get('code')).id

        photo = request.FILES.get('malfunction-photo')
        fault_object = request.POST.get('fault-object')
        description = request.POST.get('malfunction-description')

        try:
            MalfunctionService().malfunction_create(storage_id=storage_id, photo=photo,
                                                    fault_object=fault_object, description=description)
            messages.success(request, 'Неисправность успешно занесена в список.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect(f'/bar/malfunctions?code={request.GET.get("code")}')


class MalfunctionCompleteView(BaseView):

    def get(self, request):
        malfunction_id = request.GET.get('id')

        try:
            RepairerService().malfunction_complete(malfunction_id=malfunction_id)
            messages.success(request, 'Ваш ответ был успешно отправлен.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Malfunction.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/bar/malfunctions?code=' + request.GET.get('code'))

    def post(self, request):
        malfunction_id = request.GET.get('id')
        comment = request.POST.get('comment')

        try:
            RepairerService().malfunction_complete(malfunction_id=malfunction_id, comment=comment)
            messages.success(request, 'Ваш ответ был успешно отправлен.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, Malfunction.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/bar/malfunctions?code=' + request.GET.get('code'))


class PaysAddView(BaseView):

    def post(self, request):
        return ExpensesPageService().pays_create(request)


class PaysDeleteView(ObjectDeleteMixin):
    model = Pays


class FinesView(DataLogsMixin):
    template_name = 'bar/fines.html'
    model = Fine
    type = 2

    def _prepare_rows(self, storage: Storage, obj: int | None) -> list[model]:
        return get_fines_on_storage_by_month(storage=storage, month=obj)

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['fines'] = self._prepare_rows(storage=context.get('bar'), obj=request.GET.get('date'))
        context['month'] = get_months(get_current_time().month + int(request.GET.get('date'))) if request.GET.get(
            'date') else get_months(get_current_time().month)
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

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['information'] = get_full_information_of_day_for_data_logs(request.GET.get('date'), context['bar'])

        return context


class NeedItemsView(BaseView):
    template_name = 'bar/need_items.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "need_items": item_deficit_service.deficit_by_storage(storage_id=context['bar'].id)
        })

        return context

    def post(self, request):
        context = self.get_context_data(request)
        url = f'/bar/need_items?code={request.GET.get("code")}'

        item = request.POST.get('need_item')
        amount = request.POST.get('amount_need_item')

        storage = context.get('bar')
        if isinstance(storage, Storage):
            storage_id = storage.id
        else:
            messages.error(request, 'Заведение не найдено. Перезагрузите страницу')
            return redirect(url)

        try:
            item_deficit_service.create(storage_id=storage_id, item=item, amount=amount)
            messages.success(request, 'Заявка на нехватку успешно создана.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError) as error:
            messages.error(request, error)

        return redirect(url)


class NeedItemsReceiveView(BaseView):

    def post(self, request):
        try:
            receive_status = item_deficit_service.receive(request_id=request.GET.get('id'),
                                                          arrived_amount=request.POST.get('arrived_amount'),
                                                          comment=request.POST.get('comment'))
            if receive_status:
                messages.success(request, 'Статус успешно обновлен.')
            else:
                messages.error(request, 'Этот запрос еще не был обработан.')
        except (exceptions.FieldNotFoundError, exceptions.FieldCannotBeEmptyError, ItemDeficit.DoesNotExist) as error:
            messages.error(request, error)

        return redirect('/bar/need_items?code=' + request.GET.get('code'))


class SendReviseMessageView(BaseView):
    def post(self, request):
        context = self.get_context_data(request)
        bar_setting = context.get('setting')
        chat_id = bar_setting.tg_chat_id if bar_setting else ''

        revise_sum = request.POST.get('revise-sum')
        revise_reason = request.POST.get('revise-reason')

        message = f'Проверьте кассу\n\nРеальный остаток в кассе: {revise_sum}\nПричина разницы: {revise_reason}'
        send_message_to_telegram(chat_id=chat_id, message=message)

        return JsonResponse(data={"success": True}, status=200)
