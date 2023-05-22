from django.urls import path

from . import views

app_name = 'Purchaser'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('expense/create', views.ExpenseCreateView.as_view(), name="expense_create")
]
