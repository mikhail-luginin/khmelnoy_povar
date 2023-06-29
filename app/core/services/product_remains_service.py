from apps.lk.models import ProductRemain


def remain_get(storage_id: int, product_id: int) -> ProductRemain | None:
    return ProductRemain.objects.filter(storage_id=storage_id, product_id=product_id).first()


def add_remain(remains: dict, storage_id: int):
    for product_id, amount in remains.items():
        remain_record = remain_get(storage_id=storage_id, product_id=product_id)
        if remain_record is None:
            ProductRemain.objects.create(storage_id=storage_id, product_id=product_id, amount=amount)
        else:
            remain_record.amount = amount
            remain_record.save()


def remains_by_storage_id(storage_id: int):
    return ProductRemain.objects.filter(storage_id=storage_id)
