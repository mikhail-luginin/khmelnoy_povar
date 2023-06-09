from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', lambda x: redirect(settings.LOGIN_REDIRECT_URL)),

    path('lk/', include('apps.lk.urls')),
    path('iiko/', include('apps.iiko.urls')),
    path('bar/', include('apps.bar.urls')),
    path('repairer/', include('apps.repairer.urls')),
    path('api/', include('apps.api.urls')),
    path('purchaser/', include('apps.purchaser.urls')),
    path('admin/', include('apps.admin.urls')),
    path('brand_chief/', include('apps.brand_chief.urls')),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout')
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        re_path(r'^assets/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
    ]
