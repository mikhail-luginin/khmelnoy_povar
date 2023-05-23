from ..serializers import NavbarSerializer, RoleSerializer, ProfileSerializer, JobPlaceSerializer, PositionSerializer, \
    EmployeeSerializer, CatalogTypeSerializer, CatalogSerializer, TestQuestionSerializer, TestSerializer, \
    TestResultSerializer, TelegramChatSerializer, CardSerializer, PartnerSerializer, StatementSerializer, \
    FineSerializer, ExpenseSerializer, LogsSerializer, ItemDeficitSerializer
from ..utils import ModelViewSetMixin

from apps.lk.models import Navbar, Role, Profile, JobPlace, Position, Employee, Catalog, CatalogType, Logs, Expense, \
    Fine, Statement, Card, Partner, TelegramChat, TestResult, Test, TestQuestion, ItemDeficit


class NavbarViewSet(ModelViewSetMixin):
    queryset = Navbar.objects.all()
    serializer_class = NavbarSerializer


class RoleViewSet(ModelViewSetMixin):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class ProfileViewSet(ModelViewSetMixin):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class JobPlaceViewSet(ModelViewSetMixin):
    queryset = JobPlace.objects.all()
    serializer_class = JobPlaceSerializer


class PositionViewSet(ModelViewSetMixin):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class EmployeeViewSet(ModelViewSetMixin):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        is_deleted = self.request.query_params.get('is_deleted')

        if is_deleted:
            return Employee.objects.filter(is_deleted=int(is_deleted))
        else:
            return self.queryset


class CatalogTypeViewSet(ModelViewSetMixin):
    queryset = CatalogType.objects.all()
    serializer_class = CatalogTypeSerializer


class CatalogViewSet(ModelViewSetMixin):
    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer


class TestQuestionViewSet(ModelViewSetMixin):
    queryset = TestQuestion.objects.all()
    serializer_class = TestQuestionSerializer


class TestViewSet(ModelViewSetMixin):
    queryset = Test.objects.all()
    serializer_class = TestSerializer


class TestResultViewSet(ModelViewSetMixin):
    queryset = TestResult.objects.all()
    serializer_class = TestResultSerializer


class TelegramChatViewSet(ModelViewSetMixin):
    queryset = TelegramChat.objects.all()
    serializer_class = TelegramChatSerializer


class PartnerViewSet(ModelViewSetMixin):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer


class CardViewSet(ModelViewSetMixin):
    queryset = Card.objects.all()
    serializer_class = CardSerializer


class StatementViewSet(ModelViewSetMixin):
    queryset = Statement.objects.all()
    serializer_class = StatementSerializer


class FineViewSet(ModelViewSetMixin):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer


class ExpenseViewSet(ModelViewSetMixin):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer


class LogsViewSet(ModelViewSetMixin):
    queryset = Logs.objects.all()
    serializer_class = LogsSerializer


class ItemDeficitViewSet(ModelViewSetMixin):
    queryset = ItemDeficit.objects.all()
    serializer_class = ItemDeficitSerializer

    def get_queryset(self):
        status = self.request.query_params.get('status')

        if status:
            return ItemDeficit.objects.filter(status=int(status))
        else:
            return self.queryset
