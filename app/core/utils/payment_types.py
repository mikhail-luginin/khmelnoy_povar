from django.conf import settings

from apps.bar.models import Catalog


def get_nal_category() -> Catalog:
    return Catalog.objects.get(name=settings.PAYMENT_TYPE_NAL)


def get_bn_category() -> Catalog:
    return Catalog.objects.get(name=settings.PAYMENT_TYPE_BN)
