from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from . import views  # Import widoków z lokalnej aplikacji
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetConfirmView, blog, blog_detail, blog_create  # Poprawiony import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),  # Widok logowania (formularz)
    path('blog/', views.blog, name='blog'),  # Ścieżka do widoku bloga
    path('blog/<int:post_id>/', blog_detail, name='blog_detail'),  # Szczegóły postu
    path('blog/create/', blog_create, name='blog_create'),  # Tworzenie postu
    path('forum/', views.forum, name='forum'),

    # Ścieżki związane z resetowaniem hasła
    path('account/password_reset/', auth_views.PasswordResetView.as_view(template_name='reset_password.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='reset_password_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),  # Używamy niestandardowego widoku
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_password_complete.html'), name='password_reset_complete'),

    # Ścieżki rejestracji i aktywacji konta
    path('account/register/', views.register, name='register'),  # Widok dla rejestracji
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),  # Widok aktywacji konta

    # Ścieżka logowania
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),

    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),

    path('account_management/', views.account_management, name='account_management'),
    path('toggle_admin/<int:user_id>/', views.toggle_admin, name='toggle_admin'),
    path('toggle_active/<int:user_id>/', views.toggle_active, name='toggle_active'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('account_management/update_role/<int:user_id>/', views.update_user_role, name='update_user_role'),
    path('account_management/toggle_activation/<int:user_id>/', views.toggle_user_activation, name='toggle_user_activation'),
]

# Obsługa plików multimedialnych (zdjęcia profilowe)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Obsługa plików statycznych w trybie deweloperskim
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])