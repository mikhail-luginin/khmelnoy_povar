from rest_framework import serializers

from apps.iiko.models import Category, Storage, Supplier, Product, PaymentType, Discount


class StorageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Storage
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    is_income = serializers.CharField(source='get_is_income_display')
    is_sales = serializers.CharField(source='get_is_sales_display')
    is_remains = serializers.CharField(source='get_is_remains_display')


    class Meta:
        model = Category
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(many=True)
    is_revise = serializers.CharField(source='get_is_revise_display')

    class Meta:
        model = Supplier
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(default='Не привязана', source='category.name')
    supplier_name = serializers.CharField(default='Не привязан', source='supplier.name')

    class Meta:
        model = Product
        fields = '__all__'


class PaymentTypeSerializer(serializers.ModelSerializer):
    is_active = serializers.CharField(source='get_is_active_display')

    class Meta:
        model = PaymentType
        fields = '__all__'


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = '__all__'
