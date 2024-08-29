from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path

from . import views  # Lub innej aplikacji, gdzie masz views.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('blog/', views.blog, name='blog'),
    path('forum/', views.forum, name='forum'),
]

# Obsługa plików statycznych w trybie deweloperskim
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])