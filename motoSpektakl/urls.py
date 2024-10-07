from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetConfirmView, blog, blog_detail, blog_create

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('account/', views.account, name='account'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('blog/create/', blog_create, name='blog_create'),
    path('blog/<int:post_id>/like/', views.add_vote, {'vote_type': 'like'}, name='post_like'),
    path('blog/<int:post_id>/dislike/', views.add_vote, {'vote_type': 'dislike'}, name='post_dislike'),
    path('blog/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('blog/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('blog_management/add_post/', views.add_post, name='add_post'),
    path('forum/', views.forum, name='forum'),
    path('forum/<int:thread_id>/', views.forum_detail, name='forum_detail'),
    path('forum/add_thread/', views.add_thread, name='add_thread'),
    path('forum/<int:thread_id>/add_comment/', views.add_comment, name='add_comment'),
    path('forum/<int:thread_id>/edit/', views.edit_thread, name='edit_thread'),
    path('forum/<int:thread_id>/delete/', views.delete_thread, name='delete_thread'),
    path('forum/<int:thread_id>/like/', views.vote_on_thread, {'vote_type': 'like'}, name='thread_like'),
    path('forum/<int:thread_id>/dislike/', views.vote_on_thread, {'vote_type': 'dislike'}, name='thread_dislike'),
    path('account/password_reset/', auth_views.PasswordResetView.as_view(template_name='reset_password.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='reset_password_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='reset_password_complete.html'), name='password_reset_complete'),
    path('account/register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
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
    path('blog_management/', views.blog_management, name='blog_management'),
    path('comment/edit/<int:comment_id>/', views.comment_edit, name='comment_edit'),
    path('comment/delete/<int:comment_id>/', views.comment_delete, name='comment_delete'),
    path('blog/<int:post_id>/comment/edit/<int:comment_id>/', views.blog_comment_edit, name='edit_comment'),
    path('blog/<int:post_id>/comment/delete/<int:comment_id>/', views.blog_comment_delete, name='delete_comment'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)