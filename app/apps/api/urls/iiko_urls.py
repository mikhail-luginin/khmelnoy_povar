from rest_framework.routers import SimpleRouter

from ..views import iiko_views

router = SimpleRouter()
router.register('storages', iiko_views.StorageViewSet)
router.register('categories', iiko_views.CategoryViewSet)
router.register('suppliers', iiko_views.SupplierViewSet)
router.register('products', iiko_views.ProductViewSet)
router.register('payment-types', iiko_views.PaymentTypeViewSet)
router.register('discounts', iiko_views.DiscountViewSet)

urls = router.urls
