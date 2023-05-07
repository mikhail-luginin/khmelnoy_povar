from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect

from core.utils import ObjectEditMixin, BaseLkView

from apps.iiko.models import Product, Supplier, Category, PaymentType
from apps.iiko.services.product import ProductService
from apps.iiko.services.storage import StorageService
from apps.iiko.services.supplier import SupplierService
from apps.iiko.services.category import CategoryService
from apps.iiko.services.payment_type import PaymentTypeService
from apps.iiko.services.stoplist import StoplistService


@login_required
def update_nomenclature_view(request):
    if ProductService().update():
        messages.success(request, 'Номенклатура успешно обновлена.')
    else:
        messages.error(request, 'Произошла ошибка при обновлении номенклатуры.')
    return redirect('/iiko/nomenclature')


@login_required
def update_categories_view(request):
    if CategoryService().update():
        messages.success(request, 'Категории успешно обновлены.')
    else:
        messages.error(request, 'Произошла ошибка при обновлении категорий.')
    return redirect('/iiko/categories')


@login_required
def update_suppliers_view(request):
    if SupplierService().update():
        messages.success(request, 'Поставщики успешно обновлены.')
    else:
        messages.error(request, 'Произошла ошибка при обновлении поставщиков.')
    return redirect('/iiko/suppliers')


@login_required
def update_storages_view(request):
    if StorageService().update():
        messages.success(request, 'Заведения успешно обновлены.')
    else:
        messages.error(request, 'Произошла ошибка при обновлении заведений')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def update_payment_types_view(request):
    if PaymentTypeService().update():
        messages.success(request, 'Типы платежей успешно обновлены.')
    else:
        messages.error(request, 'Произошла ошибка при обновлении типов платежей')
    return redirect('/iiko/paymenttypes')


class NomenclatureView(BaseLkView):
    template_name = 'iiko/nomenclature/index.html'


class NomenclatureEditView(ObjectEditMixin):
    model = Product
    template_name = 'iiko/nomenclature/edit.html'
    success_url = '/iiko/nomenclature'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request)
        context['suppliers'] = SupplierService().suppliers_all()
        context['categories'] = CategoryService().categories_all()

        return context


class SuppliersView(BaseLkView):
    template_name = 'iiko/suppliers/index.html'


class SupplierEditView(ObjectEditMixin):
    model = Supplier
    template_name = 'iiko/suppliers/edit.html'
    success_url = '/iiko/suppliers'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request)
        context['categories'] = CategoryService().categories_all()

        return context


class CategoriesView(BaseLkView):
    template_name = 'iiko/categories/index.html'


class CategoryEditView(ObjectEditMixin):
    model = Category
    template_name = 'iiko/categories/edit.html'
    success_url = '/iiko/categories'

    def post(self, request):
        return CategoryService().category_edit(request, self.success_url)


class PaymentTypesView(BaseLkView):
    template_name = 'iiko/paymenttypes/index.html'


class PaymentTypeEdit(ObjectEditMixin):
    model = PaymentType
    template_name = 'iiko/paymenttypes/edit.html'
    success_url = '/iiko/paymenttypes'


class StopListView(BaseLkView):
    template_name = 'iiko/stoplist.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['rows'] = StoplistService().get_stoplist_items()

        return context


class StopListUpdateView(BaseLkView):

    def get(self, request):
        if StoplistService().update():
            response = {"status": True, "rows": StoplistService().get_stoplist_items()}
        else:
            response = {"status": False}

        return JsonResponse(response, status=200)
