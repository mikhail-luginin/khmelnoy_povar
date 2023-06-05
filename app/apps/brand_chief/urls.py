from django.urls import path

from . import views

app_name = "BrandChief"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('malfunctions', views.MalfunctionsView.as_view(), name="malfunctions"),
    path('item_deficit', views.ItemDeficitView.as_view(), name="item_deficit")
]
