from rest_framework.routers import SimpleRouter

from ..views import bar_views

router = SimpleRouter()
router.register('money', bar_views.MoneyViewSet)
router.register('salary', bar_views.SalaryViewSet)
router.register('timetable', bar_views.TimetableViewSet)
router.register('tovar-requests', bar_views.TovarRequestViewSet)
router.register('arrivals', bar_views.ArrivalViewSet)
router.register('pays', bar_views.PaysViewSet)

urls = router.urls
