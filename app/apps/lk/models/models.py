from django.db import models
from django.contrib.auth.models import User

from . import managers

from apps.iiko.models import Storage


class Navbar(models.Model):
    link = models.CharField(max_length=64)
    text = models.CharField(max_length=64)
    app_name = models.CharField(max_length=16)


class Role(models.Model):
    name = models.CharField(max_length=32)
    can_all = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_view = models.ManyToManyField(Navbar)

    objects = managers.RoleManager()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(to=Role, on_delete=models.SET_NULL, null=True)
    tg_id = models.CharField(max_length=32, null=True)

    objects = managers.ProfileManager()


class JobPlace(models.Model):
    name = models.CharField(max_length=32)
    main_shift_oklad = models.IntegerField(default=0)
    gain_shift_oklad = models.IntegerField(default=0)


class Position(models.Model):
    name = models.CharField(max_length=32)
    args = models.JSONField(null=True)
    linked_jobs = models.ManyToManyField(JobPlace)
    priority_id = models.IntegerField()

    objects = managers.PositionManager()


class Employee(models.Model):
    STATUS_CHOICES = [
        (1, 'Кандидат'),
        (2, 'Стажер'),
        (3, 'Сотрудник'),
        (4, 'Резерв')
    ]

    code = models.CharField(max_length=64)
    photo = models.IntegerField(default=0)
    fio = models.CharField(max_length=64)
    birth_date = models.DateField(null=True)
    address = models.CharField(max_length=64, null=True)
    job_place = models.ForeignKey(JobPlace, on_delete=models.SET_NULL, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=11)
    is_deleted = models.PositiveSmallIntegerField(default=0)
    dismiss_date = models.DateField(null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=3)

    objects = managers.EmployeeManager()


class CatalogType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Catalog(models.Model):
    name = models.CharField(max_length=32)
    catalog_types = models.ManyToManyField(CatalogType)

    objects = managers.CatalogManager()


class TestQuestion(models.Model):
    text = models.CharField(max_length=128)
    is_correct = models.PositiveSmallIntegerField()


class Test(models.Model):
    created_at = models.DateField()
    name = models.CharField(max_length=32)
    questions = models.ManyToManyField(TestQuestion)
    is_ended = models.PositiveSmallIntegerField()

    objects = managers.TestManager()


class TestResult(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    test = models.ForeignKey(Test, on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    correct_answers = models.IntegerField()
    logs = models.JSONField()

    objects = managers.TestResultManager()


class TelegramChat(models.Model):
    chat_id = models.CharField(max_length=16)
    name = models.CharField(max_length=32)


class Partner(models.Model):
    name = models.CharField(max_length=128)
    inn = models.CharField(max_length=12)
    friendly_name = models.CharField(max_length=64)
    expense_type = models.ManyToManyField(Catalog)
    storage = models.ManyToManyField(Storage)

    objects = managers.PartnerManager()


class Card(models.Model):
    name = models.CharField(max_length=32)
    num = models.CharField(max_length=16)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    type = models.IntegerField()

    objects = managers.CardManager()


class Statement(models.Model):
    linked = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    document_type = models.CharField(max_length=32)
    document_number = models.IntegerField()
    date = models.DateField(null=True)
    date_write_off = models.DateField(null=True)
    date_receipt = models.DateField(null=True)
    sum = models.FloatField()
    payer = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, related_name='payer')
    recipient = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, related_name='recipient')
    payment_purpose = models.CharField(max_length=256)
    comment = models.CharField(max_length=64, null=True)

    objects = managers.StatementManager()


class Fine(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    date_at = models.DateField()
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    sum = models.IntegerField()
    reason = models.ForeignKey(Catalog, on_delete=models.SET_NULL, null=True)
    is_received = models.PositiveSmallIntegerField(default=0)

    objects = managers.FineManager()


class Expense(models.Model):
    writer = models.CharField(max_length=32)
    date_at = models.DateField()
    created_at = models.DateTimeField(auto_now=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    expense_type = models.ForeignKey(Catalog, on_delete=models.SET_NULL, null=True, related_name='type')
    expense_source = models.ForeignKey(Catalog, on_delete=models.SET_NULL, null=True, related_name='source')
    payment_receiver = models.CharField(max_length=64, null=True)
    sum = models.FloatField()
    comment = models.CharField(max_length=128)

    objects = managers.ExpenseManager()


class Logs(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=128)
    page = models.CharField(max_length=128)
    action = models.CharField(max_length=32)
    comment = models.CharField(max_length=128, null=True)
    is_bar = models.BooleanField(default=False)


class ItemDeficit(models.Model):
    STATUS_CHOICES = [
        (1, 'Создано'),
        (2, 'Отправлено'),
        (3, 'Получено')
    ]

    created_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(to=Profile, on_delete=models.SET_NULL, null=True)
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    item = models.CharField(max_length=128)
    amount = models.CharField(max_length=32)
    receive_date = models.DateTimeField(null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)

    objects = managers.ItemDeficitManager()
