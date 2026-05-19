from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Profile, Follow, Notification

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'avatar', 'banner', 'bio', 'website', 'github', 'linkedin', 'twitter', 'joined_date', 'posts_count', 'followers_count', 'following_count']

    def get_posts_count(self, obj):
        return Post.objects.filter(user=obj.user).count()

    def get_followers_count(self, obj):
        return Follow.objects.filter(following=obj.user).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj.user).count()

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    likes_count = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'username', 'parent', 'comment_text', 'name', 'email', 'likes_count', 'replies', 'created_at']
        read_only_fields = ['user', 'username']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_replies(self, obj):
        # Nested comment replies
        serializer = CommentSerializer(obj.replies.filter(is_approved=True), many=True)
        return serializer.data

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.username', read_only=True)
    author_avatar = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    bookmarks_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    read_time = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'author', 'author_avatar', 'text', 'slug', 'description', 'photo', 'category', 'is_draft', 'is_featured', 'views_count', 'likes_count', 'bookmarks_count', 'comments_count', 'seo_title', 'seo_description', 'read_time', 'created_at', 'updated_at']
        read_only_fields = ['user', 'views_count', 'slug']

    def get_author_avatar(self, obj):
        if hasattr(obj.user, 'profile') and obj.user.profile.avatar:
            return obj.user.profile.avatar.url
        return None

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_bookmarks_count(self, obj):
        return obj.bookmarks.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'sender', 'sender_username', 'notification_type', 'post', 'comment', 'text', 'is_read', 'created_at']
