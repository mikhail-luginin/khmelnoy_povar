from django.urls import path

from . import views

app_name = "Bar"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('timetable/delete', views.TimetableDeleteView.as_view(), name="timetable_delete"),

    path('expenses', views.ExpensesView.as_view(), name="expenses"),
    path('expenses/delete', views.ExpenseDeleteView.as_view(), name="expense_delete"),

    path('pays/add', views.PaysAddView.as_view(), name="pays_add"),
    path('pays/delete', views.PaysDeleteView.as_view(), name="pays_delete"),

    path('other', views.OtherView.as_view(), name="other"),

    path('salary', views.SalaryView.as_view(), name="salary"),
    path('salary/calculation', views.SalaryCalculationView.as_view(), name="salary_calculation"),
    path('salary/retired_employees', views.SalaryForRetiredEmployeesView.as_view(), name="salary_for_retired_employees"),
    path('salary/retired_employees/accrue', views.salary_for_retired_employee_accrue_view,
         name="salary_for_retired_employee_accrue"),

    path('requests/beer', views.TovarRequestBeerView.as_view(), name="tovar_request_beer"),
    path('requests/bar', views.TovarRequestBarView.as_view(), name="tovar_request_bar"),
    path('requests/products', views.TovarRequestProductsView.as_view(), name="tovar_request_products"),
    path('requests/hoz', views.TovarRequestHozView.as_view(), name="tovar_request_hoz"),
    path('requests/box', views.TovarRequestBoxView.as_view(), name="tovar_request_box"),
    path('requests/delete', views.TovarRequestDeleteView.as_view(), name="tovar_request_delete"),

    path('arrivals/beer', views.ArrivalBeerView.as_view(), name="arrival_beer"),
    path('arrivals/drinks', views.ArrivalDrinkView.as_view(), name="arrival_drink"),
    path('arrivals/delete', views.ArrivalDeleteView.as_view(), name="arrival_delete"),

    path('employee', views.EmployeeView.as_view(), name="employee"),
    path('employee/add', views.AddEmployeeView.as_view(), name="add_employee"),

    path('inventory/bar', views.InventoryBarView.as_view(), name="inventory_bar"),
    path('inventory/ware', views.InventoryWareView.as_view(), name="inventory_ware"),

    path('malfunctions', views.MalfunctionsView.as_view(), name="malfunctions"),

    path('fines', views.FinesView.as_view(), name="fines"),

    path('data_logs/timetable', views.TimetableDataLogView.as_view(), name="data_log_timetable"),
    path('data_logs/arrivals', views.ArrivalsDataLogView.as_view(), name="data_log_arrivals"),
    path('data_logs/end_day', views.EndDayDataLogView.as_view(), name="data_log_end_day"),

    path('need_items', views.NeedItemsView.as_view(), name="need_items"),
    path('need_items/receive', views.NeedItemsReceiveView.as_view(), name="receive_need_item"),

    path('end_day', views.EndDayView.as_view(), name="end_day")
]
