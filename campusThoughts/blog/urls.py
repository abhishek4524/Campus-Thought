from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views, api_views
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# API Router configuration
router = DefaultRouter()
router.register(r'posts', api_views.PostViewSet, basename='api_posts')
router.register(r'comments', api_views.CommentViewSet, basename='api_comments')
router.register(r'profiles', api_views.ProfileViewSet, basename='api_profiles')
router.register(r'notifications', api_views.NotificationViewSet, basename='api_notifications')

urlpatterns = [
    # Core Front-End HTML Views
    path('', views.home, name='home'),
    path('create/', views.BlogCreateView.as_view(), name='blog_create'),
    path('post/<slug:slug>/', views.full_blog, name='full_blog'),
    path('<int:post_id>/edit/', views.BlogEditView.as_view(), name='blog_edit'),
    path('autosave/', views.BlogAutosaveView.as_view(), name='blog_autosave'),
    path('<int:post_id>/delete/', views.blog_delete, name='blog_delete'),
    
    # User Profile & Follows
    path('user/<str:username>/', views.profile_detail, name='profile_detail'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/bookmark-toggle/<int:post_id>/', views.bookmark_toggle, name='bookmark_toggle'),
    path('profile/like-toggle/<int:post_id>/', views.like_toggle, name='like_toggle'),
    path('user/<str:username>/follow-toggle/', views.follow_toggle, name='follow_toggle'),
    path('bookmarks/', views.bookmarks_dashboard, name='bookmarks_dashboard'),
    
    # Advanced Search, Notifications, Theme
    path('search/', views.search, name='search'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/read-all/', views.notifications_read_all, name='notifications_read_all'),
    
    # Custom Admin & Moderator Dashboards
    path('dashboard/', views.custom_admin_dashboard, name='admin_dashboard'),
    path('dashboard/user-ban/<int:user_id>/', views.admin_user_ban, name='admin_user_ban'),
    path('dashboard/post-approve/<int:post_id>/', views.admin_post_approve, name='admin_post_approve'),
    path('dashboard/comment-moderate/<int:comment_id>/', views.admin_comment_moderate, name='admin_comment_moderate'),
    path('dashboard/settings/', views.admin_site_settings, name='admin_site_settings'),
    path('dashboard/login-logs/', views.admin_login_logs, name='admin_login_logs'),
    
    # Auth Views
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Secure Password Reset with OTP & Token Invalidation
    path('password-reset/', views.forgot_password, name='password_reset'),
    path('password-reset/verify-otp/', views.verify_otp, name='verify_otp'),
    path('password-reset/confirm/', views.reset_password, name='reset_password'),

    # REST APIs & SimpleJWT Authentication
    path('api/', include(router.urls)),
    path('api/register/', api_views.APIRegisterView.as_view(), name='api_register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]