from django.urls import path

from . import views

app_name = "Repairer"

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('malfunction/complete', views.MalfunctionComplete.as_view(), name="malfunction_complete")
]
