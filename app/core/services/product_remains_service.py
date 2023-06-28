from apps.lk.models import ProductRemain


def add_remain(remains: dict, storage_id: int):
    for product_id, amount in remains.items():
        ProductRemain.objects.create(storage_id=storage_id, product_id=product_id, amount=amount)


def remains_by_storage_id(storage_id: int):
    return ProductRemain.objects.filter(storage_id=storage_id)
