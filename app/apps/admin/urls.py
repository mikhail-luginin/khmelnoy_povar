from django.urls import path

from . import views

app_name = 'Admin'

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),

    path('role/create', views.RoleCreateView.as_view(), name="role_create"),
    path('role/edit', views.RoleEditView.as_view(), name="role_edit"),
    path('role/delete', views.RoleDeleteView.as_view(), name="role_delete"),

    path('page/create', views.PageCreateView.as_view(), name="page_create"),
    path('page/edit', views.PageEditView.as_view(), name="page_edit"),
    path('page/delete', views.PageDeleteView.as_view(), name="page_delete"),

    path('user/create', views.UserCreateView.as_view(), name="user_create"),
    path('user/edit', views.UserEditView.as_view(), name="user_edit"),
    path('user/delete', views.UserDeleteView.as_view(), name="user_delete"),
]
