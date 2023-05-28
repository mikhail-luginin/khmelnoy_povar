from rest_framework import serializers

from apps.lk.models import Navbar, Role, Profile, JobPlace, Position, Employee, Catalog, CatalogType, Logs, Expense, \
    Fine, Statement, Card, Partner, TelegramChat, TestResult, Test, TestQuestion, ItemDeficit
from apps.repairer.models import Malfunction


class NavbarSerializer(serializers.ModelSerializer):

    class Meta:
        model = Navbar
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = '__all__'


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = '__all__'


class JobPlaceSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobPlace
        fields = '__all__'


class PositionSerializer(serializers.ModelSerializer):
    oklad = serializers.SerializerMethodField()

    def get_oklad(self, obj):
        return obj.args['oklad']

    class Meta:
        model = Position
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    job = serializers.CharField(source='job_place.name')
    storage_name = serializers.CharField(source='storage.name')
    active_status = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')
    employee_fio = serializers.SerializerMethodField()

    def get_active_status(self, obj):
        if obj.is_deleted == 0:
            return 'Активный'
        else:
            return f'Уволен ({obj.dismiss_date})'

    def get_employee_fio(self, obj):
        return f'<a href="/bar/employee?employee_code={obj.code}">{obj.fio}</a>'

    class Meta:
        model = Employee
        fields = '__all__'


class CatalogTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CatalogType
        fields = '__all__'


class CatalogSerializer(serializers.ModelSerializer):
    catalog_types = serializers.StringRelatedField(many=True)

    class Meta:
        model = Catalog
        fields = '__all__'


class TestQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestQuestion
        fields = '__all__'


class TestResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestResult
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Test
        fields = '__all__'


class TelegramChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = TelegramChat
        fields = '__all__'


class PartnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Partner
        fields = '__all__'


class CardSerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')

    class Meta:
        model = Card
        fields = '__all__'


class StatementSerializer(serializers.ModelSerializer):
    linked = serializers.CharField(source='linked.name', allow_null=True, default='Не привязана')
    payer_name = serializers.CharField(source='payer.name', allow_null=True, default='Не привязан')
    recipient_name = serializers.CharField(source='recipient.name', allow_null=True, default='Не привязан')

    class Meta:
        model = Statement
        fields = '__all__'


class FineSerializer(serializers.ModelSerializer):
    employee_fio = serializers.CharField(source='employee.fio')
    reason_name = serializers.CharField(source='reason.name')

    class Meta:
        model = Fine
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')
    expense_type_name = serializers.CharField(source='expense_type.name', allow_null=True, default='Не указана')
    expense_source_name = serializers.CharField(source='expense_source.name', allow_null=True, default='Не указан')

    class Meta:
        model = Expense
        fields = '__all__'


class LogsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Logs
        fields = '__all__'


class ItemDeficitSerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')
    owner_fio = serializers.CharField(source='owner.user.username',
                                      allow_null=True, default='Не привязан')

    class Meta:
        model = ItemDeficit
        fields = '__all__'


class MalfunctionSerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')
    photo_link = serializers.CharField(source='photo.url')

    class Meta:
        model = Malfunction
        fields = '__all__'
