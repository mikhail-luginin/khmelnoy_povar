from apps.api.serializers import CategorySerializer, StorageSerializer, SupplierSerializer, ProductSerializer, \
    PaymentTypeSerializer, DiscountSerializer
from apps.api.mixins import ModelViewSetMixin
from apps.iiko.models import Category, Storage, Supplier, Product, PaymentType, Discount


class StorageViewSet(ModelViewSetMixin):
    queryset = Storage.objects.all()
    serializer_class = StorageSerializer


class CategoryViewSet(ModelViewSetMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SupplierViewSet(ModelViewSetMixin):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class ProductViewSet(ModelViewSetMixin):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class PaymentTypeViewSet(ModelViewSetMixin):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer


class DiscountViewSet(ModelViewSetMixin):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
