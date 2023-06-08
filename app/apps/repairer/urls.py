from django.urls import path

from . import views

app_name = "Repairer"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('malfunction/complete', views.MalfunctionComplete.as_view(), name="malfunction_complete"),

    path('item_deficit', views.ItemDeficitView.as_view(), name="item_deficit"),
    path('item_deficit/send', views.ItemDeficitSendView.as_view(), name="item_deficit_send")
]
