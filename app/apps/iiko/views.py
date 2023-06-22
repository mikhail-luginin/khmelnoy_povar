from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect

from core.services.product_request import ProductRequestService
from core.exceptions import FieldNotFoundError, FieldCannotBeEmptyError
from core.mixins import ObjectEditMixin, BaseLkView

from apps.iiko.models import Product, Supplier, Category, PaymentType
from core.services.product import ProductService
from core.services.storage import StorageService
from core.services.supplier import SupplierService
from core.services.category import CategoryService
from core.services.payment_type import PaymentTypeService
from core.services.stoplist import StoplistService
from core.services.terminal import TerminalService


@login_required
def update_nomenclature_view(request):
    ProductService().update()
    messages.success(request, 'Номенклатура успешно обновлена.')
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
        context['row'] = Product.objects.filter(id=request.GET.get('id')).first()
        return context

    def post(self, request):
        row_id = request.GET.get('id')
        minimal = request.POST.get('minimal')
        for_order = request.POST.get('for_order')
        category_id = request.POST.get('category_id')
        supplier_id = request.POST.get('supplier_id')

        try:
            ProductService().nomenclature_edit(row_id=row_id, minimal=minimal, for_order=for_order,
                                             category_id=category_id, supplier_id=supplier_id)
            messages.success(request, 'Продукт успешно отредактирован :)')
            url = '/iiko/nomenclature'
        except FieldNotFoundError as error:
            url = f'/iiko/nomenclature/edit?id={row_id}'
            messages.error(request, error)
        except ValueError:
            url = f'/iiko/nomenclature/edit?id={row_id}'
            messages.error(request, 'В полях "Мин. кол-во" и "Для заказа" должны быть только цифры.')

        return redirect(url)


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

    def post(self, request):
        row_id = request.GET.get('id')
        friendly_name = request.POST.get('friendly_name')
        category = request.POST.getlist('category_id')
        is_revise = request.POST.get('is_revise')

        try:
            SupplierService().supplier_edit(row_id=row_id, friendly_name=friendly_name,
                                            category=category, is_revise=is_revise)
            messages.success(request, 'Поставщик успешно отредактирован :)')
            url = '/iiko/suppliers'
        except (FieldNotFoundError, FieldCannotBeEmptyError) as error:
            messages.error(request, error)
            url = f'/iiko/suppliers/edit?id={row_id}'

        return redirect(url)


class CategoriesView(BaseLkView):
    template_name = 'iiko/categories/index.html'


class CategoryEditView(ObjectEditMixin):
    model = Category
    template_name = 'iiko/categories/edit.html'
    success_url = '/iiko/categories'

    def post(self, request):
        row_id = request.GET.get('id')
        is_income = request.POST.get('is_income')
        is_sales = request.POST.get('is_sales')
        is_remains = request.POST.get('is_remains')

        try:
            CategoryService().category_edit(row_id=row_id, is_income=is_income,
                                            is_sales=is_sales, is_remains=is_remains)
            messages.success(request, 'Категория успешно отредактирована :)')
            url = '/iiko/categories'
        except FieldNotFoundError as error:
            messages.error(request, error)
            url = f'/iiko/categories/edit?id={row_id}'

        return redirect(url)

class PaymentTypesView(BaseLkView):
    template_name = 'iiko/paymenttypes/index.html'


class PaymentTypeEdit(ObjectEditMixin):
    model = PaymentType
    template_name = 'iiko/paymenttypes/edit.html'
    success_url = '/iiko/paymenttypes'

    def post(self, request):
        row_id = request.GET.get('id')
        is_active = request.POST.get('is_active')

        try:
            PaymentTypeService().paymenttype_edit(row_id=row_id, is_active=is_active)
            messages.success(request, f'Тип оплаты успешно отредактирован :)')
            url = '/iiko/paymenttypes'
        except FieldNotFoundError as error:
            messages.success(request, error)
            url = f'/iiko/paymenttypes/edit?id={row_id}'

        return redirect(url)


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


def terminals_update_view(request):
    TerminalService().update()
    messages.success(request, 'Терминалы успешно обновлены.')
    return redirect('/iiko/terminals')


class ProductRequestView(BaseLkView):
    template_name = 'iiko/product_request.html'

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "categories": CategoryService().remain_categories()
        })

        return context

    def post(self, request):
        category = request.POST.get('category')
        date_at = request.POST.get('date_at')

        print(ProductRequestService().remain_products(category=category, date_at=date_at))

        return JsonResponse({
            "data": ProductRequestService().remain_products(category=category, date_at=date_at)
        }, status=200)


class ProductRequestGenerateMessageView(BaseLkView):

    def get(self, request):
        date_at = request.GET.get('date_at')

        message = ProductRequestService().generate_message(date_at=date_at)
        return JsonResponse({"message": message}, status=200)
