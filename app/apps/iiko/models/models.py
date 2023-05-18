from django.db import models

from . import managers


class Storage(models.Model):
    code = models.CharField(max_length=64, null=True)
    storage_id = models.CharField(max_length=64, null=True)
    point_of_sale = models.CharField(max_length=64, null=True)
    name = models.CharField(max_length=64)
    entity = models.CharField(max_length=64)
    district = models.CharField(max_length=8)
    is_hide = models.PositiveSmallIntegerField()
    is_office = models.PositiveSmallIntegerField()


class Category(models.Model):
    CATEGORY_CHOICES = [
        (0, 'Не привязано'),
        (1, 'Привязано')
    ]

    category_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    is_income = models.BooleanField(default=False, choices=CATEGORY_CHOICES)
    is_sales = models.BooleanField(default=False, choices=CATEGORY_CHOICES)
    is_remains = models.BooleanField(default=False, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

class Supplier(models.Model):
    SUPPLIERS_CHOICES = [
        (0, 'Не привязан'),
        (1, 'Привязан')
    ]

    supplier_id = models.CharField(max_length=64)
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=64)
    deleted = models.BooleanField()
    category = models.ManyToManyField(to=Category)
    friendly_name = models.CharField(max_length=32, null=True)
    is_revise = models.PositiveSmallIntegerField(default=0, choices=SUPPLIERS_CHOICES)

    objects = managers.SupplierManager()


class Product(models.Model):
    product_id = models.CharField(max_length=128)
    parent_id = models.CharField(max_length=128)
    name = models.CharField(max_length=128, null=True)
    num = models.CharField(max_length=64, null=True)
    code = models.CharField(max_length=64, null=True)
    type = models.CharField(max_length=64, null=True)
    main_unit = models.CharField(max_length=64, null=True)
    category = models.ForeignKey(to=Category, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(to=Supplier, on_delete=models.SET_NULL, null=True)
    minimal = models.IntegerField(null=True)
    for_order = models.IntegerField(null=True)

    objects = managers.ProductManager()


class PaymentType(models.Model):
    PAYMENT_TYPE_CHOICES = [
        (0, 'Неактивен'),
        (1, 'Активен')
    ]
    payment_id = models.CharField(max_length=64)
    code = models.CharField(max_length=8, null=True)
    name = models.CharField(max_length=64)
    is_active = models.PositiveSmallIntegerField(choices=PAYMENT_TYPE_CHOICES)


class Discount(models.Model):
    date_at = models.DateField()
    storage = models.ForeignKey(to=Storage, on_delete=models.SET_NULL, null=True)
    order_num = models.IntegerField()
    discount_percent = models.IntegerField()
    order_sum = models.IntegerField()
    order_sum_after_discount = models.IntegerField()
    discount_type = models.CharField(max_length=32)
    discount_owner = models.CharField(max_length=32)
    is_deleted = models.PositiveSmallIntegerField()

    objects = managers.DiscountManager()


class StopList(models.Model):
    date_at = models.DateTimeField()
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    storage = models.ForeignKey(to=Storage, on_delete=models.SET_NULL, null=True)

    objects = managers.StopListManager()
