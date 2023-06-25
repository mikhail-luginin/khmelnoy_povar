from django.urls import path

from .views import *

app_name = 'IIKO'

urlpatterns = [
    path('nomenclature', NomenclatureView.as_view(), name='nomenclature'),
    path('nomenclature/edit', NomenclatureEditView.as_view(), name='nomenclature_edit'),
    path('nomenclature/update', update_nomenclature_view, name='nomenclature_update'),

    path('suppliers', SuppliersView.as_view(), name='suppliers'),
    path('suppliers/edit', SupplierEditView.as_view(), name='supplier_edit'),
    path('suppliers/update', update_suppliers_view, name="suppliers_update"),

    path('categories', CategoriesView.as_view(), name='categories'),
    path('categories/edit', CategoryEditView.as_view(), name='category_edit'),
    path('categories/update', update_categories_view, name="categories_update"),

    path('paymenttypes', PaymentTypesView.as_view(), name='paymenttypes'),
    path('paymenttypes/edit', PaymentTypeEdit.as_view(), name='paymenttype_edit'),
    path('paymenttypes/update', update_payment_types_view, name="paymenttypes_update"),

    path('storages/update', update_storages_view, name="storages_update"),

    path('stoplist', StopListView.as_view()),
    path('stoplist/update', StopListUpdateView.as_view(), name="stoplist_update"),

    path('terminals/update', terminals_update_view, name="terminals_update"),

    path('requests/product', ProductRequestView.as_view(), name="product_request"),
    path('requests/product/generate_message', ProductRequestGenerateMessageView.as_view(),
         name="product_request_generate_message"),

    path('online_tables', OnlineTablesView.as_view()),
    path('online_tables_by_order_num', OnlineTableByOrderNumView.as_view()),
    path('temp/online_tables', OnlineTablesTempView.as_view()),

    path('discounts/types/update', DiscountTypeUpdateView.as_view())
]
