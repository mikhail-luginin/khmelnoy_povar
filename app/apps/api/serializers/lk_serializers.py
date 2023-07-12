from rest_framework import serializers

from apps.lk.models import Navbar, Role, Profile, JobPlace, Position, Employee, Catalog, CatalogType, Log, Expense, \
    Fine, Statement, Card, Partner, TelegramChat, TestResult, Test, TestQuestion, ItemDeficit, Review, ExpenseStatus, \
    FAQ, FAQTag
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

    class Meta:
        model = Position
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    job = serializers.CharField(source='job_place.name', default='Не привязана', allow_null=True)
    storage_name = serializers.CharField(source='storage.name', default='Не привязано', allow_null=True)
    active_status = serializers.SerializerMethodField(allow_null=True)
    status = serializers.CharField(source='get_status_display', default='Сотрудник', allow_null=True)
    employee_fio = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    reviews_count = serializers.CharField(source='reviews.count', default=0)

    def get_active_status(self, obj):
        if obj.is_deleted == 0:
            return 'Активный'
        else:
            return f'Уволен ({obj.dismiss_date})'

    def get_photo(self, obj):
        if obj.photo:
            return obj.photo.url
        return ''

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
    storage_name = serializers.CharField(source='storage.name', allow_null=True, default='Не привязано')

    class Meta:
        model = Card
        fields = '__all__'


class StatementSerializer(serializers.ModelSerializer):
    linked = serializers.CharField(source='linked.name', allow_null=True, default='Не привязано')
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


class ExpenseStatusSerializer(serializers.ModelSerializer):
    success = serializers.CharField(source='get_success_display')

    class Meta:
        model = ExpenseStatus
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')
    expense_type_name = serializers.CharField(source='expense_type.name', allow_null=True, default='Не указана')
    expense_source_name = serializers.CharField(source='expense_source.name', allow_null=True, default='Не указан')
    expense_status = serializers.SerializerMethodField()
    expense_status_comments = serializers.SerializerMethodField()

    def get_expense_status(self, obj):
        return ExpenseStatus.objects.filter(expense_id=obj.id).values()

    def get_expense_status_comments(self, obj):
        expense_status = ExpenseStatus.objects.filter(expense_id=obj.id).first()
        if expense_status:
            return expense_status.comments
        return ''

    class Meta:
        model = Expense
        fields = '__all__'


class LogsSerializer(serializers.ModelSerializer):
    action_name = serializers.CharField(source='get_action_display')

    class Meta:
        model = Log
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


class ReviewSerializer(serializers.ModelSerializer):
    storage_name = serializers.CharField(source='storage.name')
    photo_link = serializers.CharField(source='photo.url')

    class Meta:
        model = Review
        fields = '__all__'


class FAQSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = FAQ
        fields = '__all__'


class FAQTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQTag
        fields = '__all__'
