from rest_framework.routers import SimpleRouter

from ..views import lk_views


router = SimpleRouter()

router.register('navbar', lk_views.NavbarViewSet)
router.register('roles', lk_views.RoleViewSet)
router.register('profiles', lk_views.ProfileViewSet)
router.register('jobplaces', lk_views.JobPlaceViewSet)
router.register('positions', lk_views.PositionViewSet)
router.register('employees', lk_views.EmployeeViewSet)
router.register('catalog', lk_views.CatalogViewSet)
router.register('catalog-types', lk_views.CatalogTypeViewSet)
router.register('test-questions', lk_views.TestQuestionViewSet)
router.register('tests', lk_views.TestViewSet)
router.register('tests-results', lk_views.TestResultViewSet)
router.register('telegram-chats', lk_views.TelegramChatViewSet)
router.register('partners', lk_views.PartnerViewSet)
router.register('cards', lk_views.CardViewSet)
router.register('statement', lk_views.StatementViewSet)
router.register('fines', lk_views.FineViewSet)
router.register('expenses', lk_views.ExpenseViewSet)
router.register('logs', lk_views.LogsViewSet)
router.register('item_deficit', lk_views.ItemDeficitViewSet)
router.register('malfunctions', lk_views.MalfunctionViewSet)
router.register('reviews', lk_views.ReviewViewSet)
router.register('faq', lk_views.FAQViewSet)

urls = router.urls
