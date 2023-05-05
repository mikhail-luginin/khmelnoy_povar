from django.db import models


class SupplierManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().prefetch_related('category')


class ProductManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('category', 'supplier')


class DiscountManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage')


class StopListManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('product', 'storage')
