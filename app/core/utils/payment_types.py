#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

from django.conf import settings

from apps.bar.models import Catalog
from core.services import catalog_service


def get_nal_category() -> Catalog | None:
    return catalog_service.get_catalog_by_name(catalog_name=settings.PAYMENT_TYPE_NAL)


def get_bn_category() -> Catalog | None:
    return catalog_service.get_catalog_by_name(catalog_name=settings.PAYMENT_TYPE_NAL)
