from rest_framework import serializers

from apps.bar.models import Pays, Arrival, TovarRequest, Timetable, Salary, Money

from core.time import get_months


class MoneySerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')

    class Meta:
        model = Money
        fields = '__all__'


class SalarySerializer(serializers.ModelSerializer):
    employee_fio = serializers.CharField(source='employee.fio')
    storage_name = serializers.CharField(source='storage.name')
    type_name = serializers.CharField(source='get_type_display')
    total_sum = serializers.SerializerMethodField()
    month_name = serializers.SerializerMethodField()
    period_name = serializers.SerializerMethodField()

    def get_total_sum(self, obj):
        return obj.oklad + obj.percent + obj.premium

    def get_month_name(self, obj):
        month = obj.month
        if month is not None:
            return get_months(month)

    def get_period_name(self, obj):
        period = obj.period
        if period == 1:
            return 'С 1 по 15 число'
        elif period == 2:
            return 'С 16 по 31 число'
        elif period == 3:
            return 'Зарплата при увольнении'

    class Meta:
        model = Salary
        fields = '__all__'


class TimetableSerializer(serializers.ModelSerializer):
    employee_fio = serializers.CharField(source='employee.fio')
    storage_name = serializers.CharField(source='storage.name')
    position_name = serializers.CharField(source='position.name')

    class Meta:
        model = Timetable
        fields = '__all__'


class TovarRequestSerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')
    product_name = serializers.CharField(source='product.name')
    supplier_name = serializers.CharField(source='supplier.name', allow_null=True, default='Поставщик не указан')
    amount = serializers.SerializerMethodField()

    def get_amount(self, obj):
        return f'{obj.product_amount} {obj.product_main_unit}'

    class Meta:
        model = TovarRequest
        fields = '__all__'


class ArrivalSerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')
    product_name = serializers.CharField(source='product.name', allow_null=True, default="Не найдено")
    supplier_name = serializers.CharField(source='supplier.name', allow_null=True, default='Поставщик не указан')
    payment_type_name = serializers.CharField(source='payment_type.name', allow_null=True, default='Тип оплаты не указан')
    pay_type_name = serializers.SerializerMethodField()

    def get_pay_type_name(self, obj):
        match obj.type:
            case 0: return 'Неоплачено'
            case 1: return 'Оплачено'
            case 2: return 'Оплачено БАР'

    class Meta:
        model = Arrival
        fields = '__all__'


class PaysSerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')
    type_name = serializers.CharField(source='get_type_display')

    class Meta:
        model = Pays
        fields = '__all__'
