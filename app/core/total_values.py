from django.db.models import Sum

from apps.iiko.models import Storage


def get_total_expenses_by_date_and_storage(storage: Storage, date_at: str, is_bn: bool) -> int:
    from django.conf import settings
    from apps.lk.models import Expense, Catalog

    source_name = settings.PAYMENT_TYPE_BN if is_bn else settings.PAYMENT_TYPE_NAL
    source = Catalog.objects.filter(name=source_name).first()
    return Expense.objects.filter(
        storage=storage,
        date_at=date_at,
        expense_source=source
    ).exclude(expense_type__name=settings.SALARY_CATEGORY).exclude(writer__contains='акупщик').aggregate(total_sum=Sum('sum'))['total_sum'] or 0


def get_total_salary_by_date_and_storage(storage: Storage, date_at: str, payslip_type: int) -> int:
    from apps.bar.models import Salary

    return Salary.objects.filter(
        storage=storage,
        date_at=date_at,
        type=payslip_type
    ).aggregate(
        total_sum=Sum('oklad') + Sum('percent') + Sum('premium')
    )['total_sum'] or 0


def get_total_payin_by_date_and_storage(storage: Storage, date_at: str) -> int:
    from apps.bar.models import Pays

    return Pays.objects.filter(
        storage=storage,
        date_at=date_at,
        type__in=[1, 5]
    ).aggregate(Sum('sum'))['sum__sum'] or 0


def get_total_payout_by_date_and_storage(storage: Storage, date_at: str) -> int:
    from apps.bar.models import Pays

    return Pays.objects.filter(
        storage=storage,
        date_at=date_at,
        type__in=[2, 4, 6]
    ).aggregate(Sum('sum'))['sum__sum'] or 0
