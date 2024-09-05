from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from . import views  # Import widoków z lokalnej aplikacji
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),  # Widok logowania (formularz)
    path('blog/', views.blog, name='blog'),
    path('forum/', views.forum, name='forum'),

    # Ścieżki związane z resetowaniem hasła
    path('account/password_reset/', auth_views.PasswordResetView.as_view(template_name='reset_password.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='reset_password_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='reset_password_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_password_complete.html'), name='password_reset_complete'),

    # Ścieżki rejestracji i aktywacji konta
    path('account/register/', views.register, name='register'),  # Widok dla rejestracji
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),  # Widok aktywacji konta

    # Ścieżka logowania
    path('login/', auth_views.LoginView.as_view(template_name='account.html'), name='login'),  # Zmieniamy login.html na account.html
]

# Obsługa plików statycznych w trybie deweloperskim
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])