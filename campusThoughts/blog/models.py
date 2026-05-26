from django.db import models
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    is_moderator = models.BooleanField(default=False)
    is_banned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Post(models.Model):
    BLOG_TYPE_CHOICE = [
        ('Lifestyle', 'Lifestyle'),
        ('Health', 'Health'),
        ('Programming', 'Programming'),
        ('Family', 'Family'),
        ('Management', 'Management'),
        ('Travel', 'Travel'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=150)  # Replaces 'title' to maintain backward compatibility
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    category = models.CharField(max_length=11, choices=BLOG_TYPE_CHOICE, default='Programming')
    is_draft = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_posts', blank=True)
    seo_title = models.CharField(max_length=150, blank=True, null=True)
    seo_description = models.TextField(blank=True, null=True)
    last_autosaved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.user.username} - {self.text[:30]}'

    def save(self, *args, **kwargs):
        if self.text and not self.slug:
            original_slug = slugify(self.text)
            unique_slug = original_slug
            num = 1
            while Post.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{original_slug}-{num}'
                num += 1
            self.slug = unique_slug

        if not self.seo_title and self.text:
            self.seo_title = self.text[:140]

        if self.description and not self.seo_description:
            self.seo_description = strip_tags(self.description)[:160]

        super().save(*args, **kwargs)

    @property
    def description_plain(self):
        return strip_tags(self.description or '')

    @property
    def word_count(self):
        return len(self.description_plain.split())

    @property
    def read_time(self):
        minutes = max(1, round(self.word_count / 200))
        return f"{minutes} min read"

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    comment_text = models.TextField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.text[:20]}'

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following_relations', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='follower_relations', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('announcement', 'Announcement'),
    ]
    recipient = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=15, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username} ({self.notification_type})"

class SiteSetting(models.Model):
    site_title = models.CharField(max_length=100, default='Campus Thoughts')
    site_logo = models.ImageField(upload_to='logo/', blank=True, null=True)
    footer_text = models.CharField(max_length=200, default='© 2026 Campus Thoughts. All rights reserved.')
    maintenance_mode = models.BooleanField(default=False)
    theme_primary_color = models.CharField(max_length=7, default='#3b82f6')

    def __str__(self):
        return "Site Configuration Settings"

class LoginActivityLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    username_attempted = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "SUCCESS" if self.is_success else "FAILED"
        return f"Login attempted by {self.username_attempted} on {self.timestamp} - {status}"


# Django Signals to automatically create profiles for new users
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure profile exists before saving
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()

class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)

    def __str__(self):
        return f"OTP for {self.email} - Code: {self.otp_code}"
