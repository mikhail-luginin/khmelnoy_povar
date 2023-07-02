#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

from apps.bar.models import Pays, Arrival, TovarRequest, Timetable, Salary, Money, ArrivalKeg
from ..serializers import MoneySerializer, SalarySerializer, TimetableSerializer, TovarRequestSerializer, \
    ArrivalSerializer, PaysSerializer, ArrivalKegSerializer
from ..utils import ModelViewSetMixin


class MoneyViewSet(ModelViewSetMixin):
    queryset = Money.objects.all()
    serializer_class = MoneySerializer


class SalaryViewSet(ModelViewSetMixin):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer


class TimetableViewSet(ModelViewSetMixin):
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer


class TovarRequestViewSet(ModelViewSetMixin):
    queryset = TovarRequest.objects.all()
    serializer_class = TovarRequestSerializer


class ArrivalViewSet(ModelViewSetMixin):
    queryset = Arrival.objects.all()
    serializer_class = ArrivalSerializer


class ArrivalKegViewSet(ModelViewSetMixin):
    queryset = ArrivalKeg.objects.all()
    serializer_class = ArrivalKegSerializer


class PaysViewSet(ModelViewSetMixin):
    queryset = Pays.objects.all()
    serializer_class = PaysSerializer
