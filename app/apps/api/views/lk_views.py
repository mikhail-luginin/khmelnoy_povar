from rest_framework.viewsets import ModelViewSet

from apps.api.serializers import NavbarSerializer, RoleSerializer, ProfileSerializer, JobPlaceSerializer, \
    PositionSerializer, \
    EmployeeSerializer, CatalogTypeSerializer, CatalogSerializer, TestQuestionSerializer, TestSerializer, \
    TestResultSerializer, TelegramChatSerializer, CardSerializer, PartnerSerializer, StatementSerializer, \
    FineSerializer, ExpenseSerializer, LogsSerializer, ItemDeficitSerializer, MalfunctionSerializer, ReviewSerializer, \
    FAQSerializer, FAQTagSerializer
from apps.api.mixins import ModelViewSetMixin

from apps.lk.models import Navbar, Role, Profile, JobPlace, Position, Employee, Catalog, CatalogType, Log, Expense, \
    Fine, Statement, Card, Partner, TelegramChat, TestResult, Test, TestQuestion, ItemDeficit, Review, FAQ, FAQTag
from apps.repairer.models import Malfunction


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
            return Employee.objects.all()


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
    queryset = Log.objects.all()
    serializer_class = LogsSerializer


class ItemDeficitViewSet(ModelViewSetMixin):
    queryset = ItemDeficit.objects.all()
    serializer_class = ItemDeficitSerializer

    def get_queryset(self):
        without_success = self.request.query_params.get('without_success')

        if without_success and without_success == '1':
            return ItemDeficit.objects.exclude(status=3)
        else:
            return ItemDeficit.objects.filter(status=3)


class MalfunctionViewSet(ModelViewSetMixin):
    queryset = Malfunction.objects.all()
    serializer_class = MalfunctionSerializer


class ReviewViewSet(ModelViewSetMixin):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class FAQViewSet(ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


class FAQTagViewSet(ModelViewSet):
    queryset = FAQTag.objects.all()
    serializer_class = FAQTagSerializer
