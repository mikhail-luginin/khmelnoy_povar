from django.db import models
from django.contrib.auth.models import User

from . import managers

from apps.iiko.models import Storage, Product


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
    main_shift_oklad_accrual = models.IntegerField(default=0)
    gain_shift_oklad_accrual = models.IntegerField(default=0)
    main_shift_oklad_receiving = models.IntegerField(default=0)
    gain_shift_oklad_receiving = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Position(models.Model):
    name = models.CharField(max_length=32)
    args = models.JSONField(null=True)
    linked_jobs = models.ManyToManyField(JobPlace)
    priority_id = models.IntegerField()

    objects = managers.PositionManager()
    
    
class Review(models.Model):
    STATUS_CHOICES = [
        (1, 'Создан'),
        (2, 'Закрыт')
    ]
    
    created_at = models.DateField(auto_now_add=True)
    review_date = models.DateField()
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    jobs = models.ManyToManyField(to=JobPlace)
    photo = models.ImageField(upload_to='reviews_photo')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)

    objects = managers.ReviewManager()


class Employee(models.Model):
    STATUS_CHOICES = [
        (1, 'Кандидат'),
        (2, 'Стажер'),
        (3, 'Сотрудник'),
        (4, 'Резерв')
    ]

    code = models.CharField(max_length=64)
    photo = models.ImageField(upload_to='employee_photo', null=True)
    fio = models.CharField(max_length=64)
    birth_date = models.DateField(null=True)
    address = models.CharField(max_length=64, null=True)
    job_place = models.ForeignKey(JobPlace, on_delete=models.SET_NULL, null=True)
    storage = models.ForeignKey(Storage, on_delete=models.SET_NULL, null=True)
    phone = models.CharField(max_length=11)
    is_deleted = models.PositiveSmallIntegerField(default=0)
    dismiss_date = models.DateField(null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=3)
    reviews = models.ManyToManyField(to=Review)

    objects = managers.EmployeeManager()

    def get_status_by_id(self, status_id: int) -> str:
        return next(item[1] for item in self.STATUS_CHOICES if item[0] == status_id)


class EmployeeLog(models.Model):
    TYPE_CHOICES = [
        (1, 'Увольнение'),
        (2, 'Восстановление'),
        (3, 'Смена статуса'),
        (4, 'Описание')
    ]

    date_at = models.DateField()
    employee = models.ForeignKey(to=Employee, on_delete=models.CASCADE)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES)
    comment = models.CharField(max_length=255)

    objects = managers.EmployeeLogManager()


class CatalogType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Catalog(models.Model):
    name = models.CharField(max_length=32)
    catalog_types = models.ManyToManyField(CatalogType)
    args = models.JSONField(default=dict)

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
    expense_types = models.ManyToManyField(Catalog)
    storages = models.ManyToManyField(Storage)

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


class Log(models.Model):
    """
        Example:
            created_at = 2023-06-07 12:20:35
            owner = CRM Гаражная 83/1 | admin | some_user_name
            entity = Иван Иванов
            row = Timetable 12 | Expense 14
            action = 1
            additional_data = Вышел на смену | Получил зарплату за Апрель с 1 по 15 число
    """

    ACTION_CHOICES = [
        (1, 'Создание записи'),
        (2, 'Редактирование записи'),
        (3, 'Удаление записи'),
        (4, 'Обновление записи'),
        (5, 'Копирование записи')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.CharField(max_length=255)
    entity = models.CharField(max_length=255)
    row = models.CharField(max_length=255)
    action = models.PositiveIntegerField(choices=ACTION_CHOICES)
    additional_data = models.CharField(max_length=255)


class ItemDeficit(models.Model):
    STATUS_CHOICES = [
        (1, 'Создано'),
        (2, 'Отправлено'),
        (3, 'Получено')
    ]

    created_at = models.DateTimeField()
    owner = models.ForeignKey(to=Profile, on_delete=models.SET_NULL, null=True)
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    item = models.CharField(max_length=128)
    amount = models.CharField(max_length=32)
    receive_date = models.DateTimeField(null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES)
    sended_amount = models.CharField(max_length=255, null=True)
    arrived_amount = models.CharField(max_length=255, null=True)
    comment = models.CharField(max_length=255, null=True)

    objects = managers.ItemDeficitManager()


class ExpenseStatus(models.Model):
    SUCCESS_CHOICES = [
        (False, 'Отказ'),
        (True, 'Принят')
    ]

    expense = models.ForeignKey(to=Expense, on_delete=models.CASCADE)
    success = models.BooleanField(choices=SUCCESS_CHOICES)
    comments = models.JSONField(default=list)

    objects = managers.ExpenseStatusManager()


class ProductRemain(models.Model):
    storage = models.ForeignKey(to=Storage, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    amount = models.IntegerField()

    objects = managers.ProductRemainManager()


class FAQTag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class FAQ(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    tags = models.ManyToManyField(to=FAQTag)

    objects = managers.FAQManager()
