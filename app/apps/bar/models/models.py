#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

from django.db import models

from apps.iiko.models import Storage, Product, Supplier, Session
from apps.lk.models import Employee, Position, Catalog
from . import managers


class Money(models.Model):
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now=True)
    date_at = models.DateField()
    sum_cash_morning = models.IntegerField()
    total_cash = models.IntegerField(null=True)
    total_bn = models.IntegerField(null=True)
    total_day = models.IntegerField(null=True)
    total_market = models.IntegerField(null=True)
    total_expenses = models.IntegerField(null=True)
    total_salary = models.IntegerField(null=True)
    total_payin = models.IntegerField(null=True)
    total_payout = models.IntegerField(null=True)
    deposit = models.IntegerField(null=True)
    sum_cash_end_day = models.IntegerField(null=True)
    calculated = models.IntegerField(null=True)
    difference = models.IntegerField(null=True)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    barmen_percent = models.FloatField(null=True)

    objects = managers.MoneyManager()


class Salary(models.Model):
    SALARY_TYPE_CHOICES = [
        (1, 'Аванс'),
        (2, 'Расчет')
    ]

    date_at = models.DateField()
    created_at = models.DateTimeField(auto_now=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    type = models.PositiveSmallIntegerField(choices=SALARY_TYPE_CHOICES)
    oklad = models.IntegerField()
    percent = models.IntegerField(default=0)
    premium = models.IntegerField(default=0)
    month = models.IntegerField(null=True)
    period = models.IntegerField(null=True)

    objects = managers.SalaryManager()

    def get_total_sum(self):
        return self.oklad + self.percent + self.premium

    def get_month_name(self):
        from core.utils.time import get_months

        return get_months(self.month)

    def get_period_name(self):
        match self.period:
            case 1: return 'С 1 по 15 число'
            case 2: return 'С 16 по 31 число'
            case 3: return 'Расчет при увольнении'


class Timetable(models.Model):
    date_at = models.DateField()
    created_at = models.DateTimeField(auto_now=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)
    oklad = models.IntegerField()
    percent = models.IntegerField(default=0)
    premium = models.IntegerField(default=0)
    fine = models.IntegerField(default=0)

    objects = managers.TimetableManager()


class TovarRequest(models.Model):
    date_at = models.DateField()
    created_at = models.DateTimeField(auto_now=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_amount = models.IntegerField()
    product_main_unit = models.CharField(max_length=32)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)

    objects = managers.TovarRequestManager()


class Arrival(models.Model):
    ARRIVAL_TYPE_CHOICES = [
        (0, 'Неоплачено'),
        (1, 'Оплачено'),
        (2, 'Оплачено БАР')
    ]

    date_at = models.DateField(null=True)
    storage = models.ForeignKey(to=Storage, on_delete=models.SET_NULL, null=True)
    num = models.CharField(max_length=64, null=True)
    supplier = models.ForeignKey(to=Supplier, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(to=Product, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField()
    sum = models.FloatField()
    type = models.PositiveSmallIntegerField(choices=ARRIVAL_TYPE_CHOICES, default=0)
    payment_date = models.DateField(null=True)
    payment_type = models.ForeignKey(to=Catalog, on_delete=models.SET_NULL, null=True)

    objects = managers.ArrivalManager()


class ArrivalInvoice(models.Model):
    ARRIVAL_TYPE_CHOICES = [
        (0, 'Неоплачено'),
        (1, 'Оплачено'),
        (2, 'Оплачено БАР')
    ]

    date_at = models.DateField()
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    number = models.CharField(max_length=255)
    supplier = models.ForeignKey(to=Supplier, on_delete=models.SET_NULL, null=True)
    sum = models.FloatField()
    type = models.PositiveSmallIntegerField(choices=ARRIVAL_TYPE_CHOICES, default=0)
    payment_date = models.DateField(null=True)
    payment_type = models.ForeignKey(to=Catalog, on_delete=models.SET_NULL, null=True)
    arrivals = models.ManyToManyField(to=Arrival)

    objects = managers.ArrivalInvoiceManager()


class ArrivalKeg(models.Model):
    invoice_number = models.CharField(max_length=255)
    gave_thirty = models.PositiveIntegerField()
    received_thirty = models.PositiveIntegerField()
    gave_fifty = models.PositiveIntegerField()
    received_fifty = models.PositiveIntegerField()


class Pays(models.Model):
    PAYS_TYPES = [
        (1, 'Внесение'),
        (2, 'Изъятие')
    ]

    date_at = models.DateField()
    created_at = models.DateTimeField(auto_now=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    type = models.PositiveSmallIntegerField(choices=PAYS_TYPES)
    from_to = models.ForeignKey(Catalog, on_delete=models.SET_NULL, null=True)
    sum = models.FloatField()
    comment = models.CharField(max_length=64)

    objects = managers.PaysManager()


class EndDayQuestions(models.Model):
    text = models.CharField(max_length=255)


class Setting(models.Model):
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    percent = models.FloatField(null=True)
    tg_chat_id = models.CharField(max_length=64, null=True)
    expenses_types_with_employees_in_comment = models.ManyToManyField(to=Catalog)
    bar_info = models.JSONField(default=dict)
    end_day_questions = models.ManyToManyField(to=EndDayQuestions)

    objects = managers.SettingManager()


class TelegramChats(models.Model):
    chat_id = models.CharField(max_length=16)
    name = models.CharField(max_length=32)
