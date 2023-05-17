from django.db import models

from . import managers

from apps.lk.models import Employee, Position, Catalog
from apps.iiko.models import Storage, Product, Supplier


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
        from core.time import get_months

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

    date_at = models.DateField()
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    num = models.CharField(max_length=64)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField()
    sum = models.FloatField()
    type = models.PositiveSmallIntegerField(choices=ARRIVAL_TYPE_CHOICES, default=0)
    payment_date = models.DateField(null=True)
    payment_type = models.ForeignKey(Catalog, on_delete=models.SET_NULL, null=True)

    objects = managers.ArrivalManager()


class Pays(models.Model):
    PAYS_TYPES = [
        (1, 'Внесение'),
        (2, 'Изъятие'),
        (4, 'Закупщик'),
        (5, 'Масло')
    ]

    date_at = models.DateField()
    created_at = models.DateTimeField(auto_now=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    type = models.PositiveSmallIntegerField(choices=PAYS_TYPES)
    sum = models.FloatField()
    comment = models.CharField(max_length=64)

    objects = managers.PaysManager()


class Setting(models.Model):
    percent = models.FloatField(null=True)
    expenses_types_with_employees_in_comment = models.ManyToManyField(to=Catalog)
    objects = managers.SettingManager()

class TelegramChats(models.Model):
    chat_id = models.CharField(max_length=16)
    name = models.CharField(max_length=32)