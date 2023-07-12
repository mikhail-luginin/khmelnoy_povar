from django.urls import path

from .views import *

app_name = 'LK'

urlpatterns = [
    path('', IndexView.as_view(), name="index"),

    path('catalog', CatalogView.as_view(), name="catalog"),
    path('catalog/add', CatalogCreateView.as_view(), name="catalog_add"),
    path('catalog/edit', CatalogEditView.as_view(), name="catalog_edit"),
    path('catalog/delete', CatalogDeleteView.as_view(), name="catalog_delete"),

    path('catalog/type/add', CatalogTypeCreateView.as_view(), name="catalog_type_add"),
    path('catalog/types/edit', CatalogTypeEditView.as_view(), name="catalog_type_edit"),
    path('catalog/types/delete', CatalogTypeDeleteView.as_view(), name="catalog_type_delete"),

    path('bars', BarsView.as_view(), name="bars"),
    path('bars/settings', BarSettingsView.as_view(), name="bars_settings"),
    path('product_remains_add', product_remains_add, name="product_remains_add"),
    path('link_question_to_bar_setting', link_question_to_bar_setting, name="link_question_to_bar_setting"),

    path('positions', PositionsView.as_view(), name="positions"),
    path('positions/edit', PositionsEditView.as_view(), name="position_edit"),
    path('positions/delete', PositionDeleteView.as_view(), name="position_delete"),

    path('jobs/add', JobAddView.as_view(), name="job_add"),

    path('bank', BankView.as_view(), name="bank"),
    path('bank/update', bank_update, name="update_bank"),
    path('bank/partners', BankPartnersView.as_view(), name="bank_partners"),
    path('bank/partners/edit', BankPartnerEditView.as_view(), name="edit_bank_partner"),
    path('bank/cards', BankCardsView.as_view(), name="bank_cards"),
    path('bank/cards/create', BankCardCreateView.as_view(), name="create_bank_card"),
    path('bank/cards/edit', BankCardEditView.as_view(), name="edit_bank_card"),

    path('money', MoneyView.as_view(), name="money"),
    path('money/update', update_money, name="update_money"),
    path('money/edit', MoneyEditView.as_view(), name="edit_money"),
    path('money/update_all', update_all_money_and_sessions, name="update_all_money"),
    path('money/differences', MoneyDifferencesView.as_view(), name="money_differences"),

    path('timetable', TimetableView.as_view(), name="timetable"),
    path('timetable/create', CreateTimetableView.as_view(), name="create_timetable"),
    path('timetable/edit', EditTimetableView.as_view(), name="edit_timetable"),
    path('timetable/delete', DeleteTimetableView.as_view(), name="delete_timetable"),
    path('timetable/update', TimetableUpdateView.as_view(), name="update_timetable"),

    path('expenses', ExpensesView.as_view(), name="expenses"),
    path('expenses/create', CreateExpenseView.as_view(), name="create_expense"),
    path('expenses/edit', EditExpenseView.as_view(), name="edit_expense"),
    path('expenses/delete', DeleteExpenseView.as_view(), name="delete_expense"),
    path('expenses/status', ExpenseStatusView.as_view(), name="status_expense"),

    path('salary', SalaryView.as_view(), name="salary"),
    path('salary/create', CreateSalaryView.as_view(), name="create_salary"),
    path('salary/edit', EditSalaryView.as_view(), name="edit_salary"),
    path('salary/delete', DeleteSalaryView.as_view(), name="delete_salary"),

    path('pays', PaysView.as_view(), name="pays"),
    path('pays/create', CreatePaysView.as_view(), name="create_pays"),
    path('pays/edit', EditPaysView.as_view(), name="edit_pays"),
    path('pays/delete', DeletePaysView.as_view(), name="delete_pays"),

    path('fines', FinesView.as_view(), name="fines"),
    path('fines/create', CreateFineView.as_view(), name="create_fine"),
    path('fines/edit', EditFinesView.as_view(), name="edit_fine"),
    path('fines/delete', DeleteFineView.as_view(), name="delete_fine"),

    path('employees', EmployeesView.as_view(), name="employees"),
    path('employees/create', CreateEmployeeView.as_view(), name="create_employee"),
    path('employees/edit', EditEmployeeView.as_view(), name="edit_employee"),
    path('employees/dismiss', DissmissEmployeeView.as_view(), name="dismiss_employee"),
    path('employees/return', ReturnToWorkEmployeeView.as_view(), name="return_employee"),

    path('tovar/arrivals', ArrivalsView.as_view(), name="tovar_arrivals"),
    path('tovar/arrivals/create', ArrivalCreateView.as_view(), name="tovar_arrival_create"),
    path('tovar/arrivals/edit', ArrivalEditView.as_view(), name="tovar_arrival_edit"),
    path('tovar/arrivals/delete', ArrivalDeleteView.as_view(), name="tovar_arrival_delete"),
    path('tovar/arrivals/invoices', ArrivalInvoicesView.as_view(), name="total_arrival_invoices"),
    path('tovar/arrivals/invoices/all', ArrivalInvoicesAllView.as_view()),
    path('tovar/requests', TovarRequestsView.as_view(), name="tovar_requests"),
    path('tovar/requests/edit', TovarRequestEditView.as_view(), name="tovar_request_edit"),
    path('tovar/requests/delete', TovarRequestDeleteView.as_view(), name="tovar_request_delete"),

    path('need_items', ItemDeficitView.as_view(), name="need_items"),
    path('need_items/create', NeedItemsCreateView.as_view(), name="need_items_create"),
    path('need_items/send', ItemDeficitSendView.as_view(), name="receive_need_item"),

    path('bars/actions', BarActionsView.as_view()),
    path('send_message_on_bar', SendMessageOnBar.as_view(), name="send_message_on_bar"),

    path('malfunctions', MalfunctionsView.as_view(), name="malfunctions"),
    path('malfunctions/create', MalfunctionCreateView.as_view(), name="malfunction_create"),
    path('malfunctions/delete', MalfunctionDeleteView.as_view(), name="malfunction_delete"),
    path('malfunctions/complete', MalfunctionCompleteView.as_view()),

    path('reviews', ReviewsView.as_view(), name="reviews"),
    path('reviews/create', review_create, name="review_create"),
    path('reviews/link_to_employee', review_link_to_employee, name="review_to_employee"),
  
    path('logs', LogsView.as_view(), name="logs"),
    path('logs/update', update_logs_view, name="update_logs"),
    path('logs/filter', LogsWithFilterView.as_view(), name="logs_with_filter"),

    path('purchaser', PurchaserView.as_view(), name='purchaser'),
    path('purchaser_get_table', get_table_for_purchaser, name='purchaser_get_table'),

    path('reports', ReportsView.as_view()),
    path('reports/money/update', ReportsMoneyUpdateView.as_view()),
    path('reports/expense_types_by_storage', ReportExpenseTypesByStorageView.as_view()),

    path('faq', FAQView.as_view(), name='faq'),
    path('faq/create', FAQCreateView.as_view(), name='create_faq'),
    path('faq/edit', FAQEditView.as_view(), name='edit_faq'),
    path('faq/delete', FAQDeleteView.as_view(), name='delete_faq'),
    path('faq/tags/create', FAQTagCreateView.as_view(), name='create_faq_tag'),
    path('faq/tags/edit', FAQTagEditView.as_view(), name='edit_faq_tag'),
    path('faq/tags/delete', FAQTagDeleteView.as_view(), name='delete_faq_tag')
]
