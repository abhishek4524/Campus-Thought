from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Profile, Follow, Notification
from .serializers import (
    UserSerializer, ProfileSerializer, PostSerializer, 
    CommentSerializer, NotificationSerializer
)

class APIRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        if not username or not password or not email:
            return Response({'error': 'Please provide username, password, and email.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class PostViewSet(viewsets.ModelSerializerViewSet if hasattr(viewsets, 'ModelSerializerViewSet') else viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_draft=False).order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'id'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object_or_404_by_id() if hasattr(self, 'get_object_or_404_by_id') else self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, id=None):
        post = self.get_object()
        user = request.user
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
            # Trigger notification
            if post.user != user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=user,
                    notification_type='like',
                    post=post,
                    text=f"{user.username} liked your post: '{post.text[:30]}'"
                )
        return Response({'liked': liked, 'likes_count': post.likes.count()})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, id=None):
        post = self.get_object()
        user = request.user
        if post.bookmarks.filter(id=user.id).exists():
            post.bookmarks.remove(user)
            bookmarked = False
        else:
            post.bookmarks.add(user)
            bookmarked = True
        return Response({'bookmarked': bookmarked, 'bookmarks_count': post.bookmarks.count()})

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(is_approved=True).order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        post = serializer.validated_data['post']
        user = self.request.user
        comment = serializer.save(user=user, name=user.username, email=user.email)
        
        # Trigger notification
        if post.user != user:
            Notification.objects.create(
                recipient=post.user,
                sender=user,
                notification_type='comment',
                post=post,
                comment=comment,
                text=f"{user.username} commented on your post: '{post.text[:30]}'"
            )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            liked = False
        else:
            comment.likes.add(user)
            liked = True
        return Response({'liked': liked, 'likes_count': comment.likes.count()})

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'user__username'

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, user__username=None):
        profile = self.get_object()
        target_user = profile.user
        follower = request.user

        if follower == target_user:
            return Response({'error': 'You cannot follow yourself.'}, status=status.HTTP_400_BAD_REQUEST)

        follow_rel = Follow.objects.filter(follower=follower, following=target_user)
        if follow_rel.exists():
            follow_rel.delete()
            following = False
        else:
            Follow.objects.create(follower=follower, following=target_user)
            following = True
            # Trigger notification
            Notification.objects.create(
                recipient=target_user,
                sender=follower,
                notification_type='follow',
                text=f"{follower.username} started following you!"
            )
        
        return Response({
            'following': following,
            'followers_count': Follow.objects.filter(following=target_user).count()
        })

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'All notifications marked as read'})
