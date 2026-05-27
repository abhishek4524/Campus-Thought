from django.contrib import admin
from .models import (
    Post, Comment, Profile, Follow,
    Notification, SiteSetting, LoginActivityLog, OTPVerification
)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'category', 'is_draft', 'is_featured', 'views_count', 'created_at')
    list_filter = ('category', 'is_draft', 'is_featured', 'created_at')
    search_fields = ('text', 'description', 'user__username')
    prepopulated_fields = {'slug': ('text',)}
    list_editable = ('is_draft', 'is_featured')
    readonly_fields = ('views_count', 'created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'comment_text', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('comment_text', 'user__username', 'post__text')
    list_editable = ('is_approved',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'is_moderator', 'is_banned', 'joined_date')
    list_filter = ('is_moderator', 'is_banned')
    search_fields = ('user__username', 'bio')
    list_editable = ('is_moderator', 'is_banned')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'sender__username', 'text')


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'maintenance_mode', 'theme_primary_color')


@admin.register(LoginActivityLog)
class LoginActivityLogAdmin(admin.ModelAdmin):
    list_display = ('username_attempted', 'ip_address', 'is_success', 'timestamp')
    list_filter = ('is_success', 'timestamp')
    search_fields = ('username_attempted', 'ip_address')
    readonly_fields = ('username_attempted', 'ip_address', 'user_agent', 'is_success', 'timestamp')


@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'otp_code', 'is_verified', 'created_at', 'expires_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('email', 'user__username')
    readonly_fields = ('otp_code', 'created_at', 'expires_at')