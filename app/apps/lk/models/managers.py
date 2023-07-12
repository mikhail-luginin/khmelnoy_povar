from django.db import models


class RoleManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().prefetch_related('can_view')


class ProfileManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('user', 'role')


class PositionManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().prefetch_related('linked_jobs')


class EmployeeManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('job_place', 'storage').prefetch_related('reviews')


class CatalogManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().prefetch_related('catalog_types')


class TestManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().prefetch_related('questions')


class TestResultManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('test', 'employee')


class PartnerManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().prefetch_related('expense_types', 'storages')


class CardManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage')


class StatementManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('linked', 'payer', 'recipient')


class FineManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('employee', 'reason')


class ExpenseManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage', 'expense_type', 'expense_source')


class ItemDeficitManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('owner', 'storage')


class ReviewManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage').prefetch_related('jobs')


class ExpenseStatusManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('expense')


class ProductRemainManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('storage', 'product')


class EmployeeLogManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().select_related('employee')


class FAQManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().prefetch_related('tags')
