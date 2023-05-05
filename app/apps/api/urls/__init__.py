from . import lk_urls
from . import bar_urls
from . import iiko_urls

urlpatterns = lk_urls.urls + bar_urls.urls + iiko_urls.urls
