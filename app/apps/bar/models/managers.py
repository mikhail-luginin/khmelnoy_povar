from django.db import models


class MoneyManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage')


class SalaryManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage', 'employee')


class TimetableManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage', 'employee', 'position')


class TovarRequestManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage', 'supplier', 'product')


class ArrivalManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage', 'supplier', 'product')


class PaysManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage')


class SettingManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().prefetch_related('expenses_types_with_employees_in_comment').select_related('storage')
