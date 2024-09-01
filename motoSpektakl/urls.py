from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from . import views  # Lub innej aplikacji, gdzie masz views.py
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('blog/', views.blog, name='blog'),
    path('forum/', views.forum, name='forum'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('account/', views.account, name='account'),  # Widok dla "Moje Konto"
    path('account/register/', views.register, name='register'),  # Widok dla rejestracji
]

# Obsługa plików statycznych w trybie deweloperskim
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])