from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
import re

from .models import Post, Comment, Profile, Follow, Notification, SiteSetting, LoginActivityLog
from .forms import BlogForm, UserRegistrationForm, CommentForm, ProfileForm

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Paginated Home View with Categories and Sorting
def home(request):
    # Fetch site settings
    site_config, _ = SiteSetting.objects.get_or_create(id=1)
    if site_config.maintenance_mode and not request.user.is_superuser:
        return render(request, 'maintenance.html', {'site_config': site_config})

    posts_query = Post.objects.filter(is_draft=False).order_by('-created_at')

    # Category filter
    category = request.GET.get('category')
    if category:
        posts_query = posts_query.filter(category=category)

    # Sorting options
    sort_by = request.GET.get('sort')
    if sort_by == 'popular':
        posts_query = posts_query.order_by('-views_count')
    elif sort_by == 'liked':
        posts_query = posts_query.annotate(num_likes=Count('likes')).order_by('-num_likes')
    elif sort_by == 'trending':
        posts_query = posts_query.annotate(num_comments=Count('comments')).order_by('-num_comments', '-views_count')

    # Pagination (10 posts per page)
    paginator = Paginator(posts_query, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch top trending posts for sidebar widget
    trending_posts = Post.objects.filter(is_draft=False).annotate(num_likes=Count('likes')).order_by('-num_likes', '-views_count')[:5]

    return render(request, 'index.html', {
        'page_obj': page_obj,
        'selected_category': category,
        'selected_sort': sort_by,
        'trending_posts': trending_posts,
        'site_config': site_config
    })

# Advanced Search View
def search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    sort_by = request.GET.get('sort', '')
    
    results = Post.objects.filter(is_draft=False)
    
    if query:
        results = results.filter(
            Q(text__icontains=query) |
            Q(description__icontains=query) |
            Q(category__icontains=query) |
            Q(user__username__icontains=query)
        ).distinct()

    if category:
        results = results.filter(category=category)

    if sort_by == 'popular':
        results = results.order_by('-views_count')
    elif sort_by == 'liked':
        results = results.annotate(num_likes=Count('likes')).order_by('-num_likes')
    else:
        results = results.order_by('-created_at')

    paginator = Paginator(results, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'search.html', {
        'page_obj': page_obj,
        'query': query,
        'selected_category': category,
        'selected_sort': sort_by
    })

# Secure Custom Login with Log Audits
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log successful attempt
        LoginActivityLog.objects.create(
            user=self.request.user,
            username_attempted=form.cleaned_data.get('username'),
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            is_success=True
        )
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        # Log failed attempt
        LoginActivityLog.objects.create(
            username_attempted=form.data.get('username', ''),
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            is_success=False
        )
        return response

def custom_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# Blog CRUD Operations
class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = BlogForm
    template_name = 'blog_form.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        post_id = self.request.POST.get('post_id') if self.request.method == 'POST' else self.request.GET.get('post_id')
        if post_id:
            draft_post = get_object_or_404(Post, pk=post_id, user=self.request.user)
            kwargs['instance'] = draft_post
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Campus Thought'
        context['autosave_endpoint'] = reverse_lazy('blog_autosave')
        context['draft'] = None
        post_id = self.request.POST.get('post_id') or self.request.GET.get('post_id')
        if post_id:
            context['post'] = get_object_or_404(Post, pk=post_id, user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_draft = form.cleaned_data.get('is_draft', False)
        if not form.instance.seo_title:
            form.instance.seo_title = form.instance.text[:140]
        if not form.instance.seo_description and form.instance.description:
            form.instance.seo_description = form.instance.description[:160]
        response = super().form_valid(form)
        return redirect('full_blog', slug=self.object.slug)

class BlogEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = BlogForm
    template_name = 'blog_form.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.user != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Campus Thought'
        context['post'] = self.object
        context['autosave_endpoint'] = reverse_lazy('blog_autosave')
        return context

    def get_success_url(self):
        return reverse_lazy('full_blog', kwargs={'slug': self.object.slug})

    def form_valid(self, form):
        form.instance.is_draft = form.cleaned_data.get('is_draft', self.object.is_draft)
        if not form.instance.seo_title:
            form.instance.seo_title = form.instance.text[:140]
        if not form.instance.seo_description and form.instance.description:
            form.instance.seo_description = form.instance.description[:160]
        return super().form_valid(form)

class BlogAutosaveView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = request.POST.copy()
        post_id = data.get('post_id')
        if post_id:
            post = get_object_or_404(Post, pk=post_id, user=request.user)
            form = BlogForm(data, request.FILES, instance=post)
        else:
            form = BlogForm(data, request.FILES)

        if not form.is_valid():
            import sys
            print(f'DEBUG autosave form invalid: {form.errors}', file=sys.stderr)
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        draft = form.save(commit=False)
        draft.user = request.user
        draft.is_draft = True
        draft.last_autosaved_at = timezone.now()
        draft.save()

        return JsonResponse({
            'success': True,
            'post_id': draft.id,
            'slug': draft.slug,
            'last_saved': draft.last_autosaved_at.strftime('%Y-%m-%d %H:%M:%S'),
            'draft': draft.is_draft,
        })

@login_required
def blog_delete(request, post_id): 
    post = get_object_or_404(Post, pk=post_id)
    if post.user != request.user and not request.user.is_superuser:
        return redirect('home')
        
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'post_confirm_delete.html', {'post': post})

# Detail view supporting nested comment processing
def full_blog(request, slug):
    post = get_object_or_404(Post, slug=slug)
    
    # Increment views count (session-based deduplication)
    viewed_key = f'viewed_post_{post.id}'
    if not request.session.get(viewed_key, False):
        post.views_count += 1
        post.save(update_fields=['views_count'])
        request.session[viewed_key] = True

    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.name = request.user.username
            comment.email = request.user.email
            
            # Nested Reply Handling
            parent_id = request.POST.get('parent_id')
            if parent_id:
                parent_comment = get_object_or_404(Comment, id=parent_id)
                comment.parent = parent_comment

            comment.save()

            # Create notification
            if post.user != request.user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment,
                    text=f"{request.user.username} commented on your article: '{post.text[:25]}'"
                )

            return redirect('full_blog', slug=post.slug)
    else:
        form = CommentForm()

    comments = post.comments.filter(parent=None, is_approved=True).order_by('-created_at')
    comment_count = post.comments.filter(is_approved=True).count()

    return render(request, 'full_blog.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'comment_count': comment_count
    })

# User Profiles and Social Actions
def profile_detail(request, username):
    target_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=target_user)
    posts = Post.objects.filter(user=target_user, is_draft=False).order_by('-created_at')
    
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()

    followers_count = Follow.objects.filter(following=target_user).count()
    following_count = Follow.objects.filter(follower=target_user).count()

    return render(request, 'profile.html', {
        'profile': profile,
        'target_user': target_user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count
    })

@login_required
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_detail', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile_edit.html', {'form': form})

# AJAX Likes/Bookmarks/Follow Toggles
@login_required
def like_toggle(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
            # Notify author
            if post.user != user:
                Notification.objects.create(
                    recipient=post.user,
                    sender=user,
                    notification_type='like',
                    post=post,
                    text=f"{user.username} liked your article: '{post.text[:25]}'"
                )
        return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})
    return JsonResponse({'error': 'POST request required'}, status=400)

@login_required
def bookmark_toggle(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        user = request.user
        if post.bookmarks.filter(id=user.id).exists():
            post.bookmarks.remove(user)
            bookmarked = False
        else:
            post.bookmarks.add(user)
            bookmarked = True
        return JsonResponse({'bookmarked': bookmarked, 'bookmarks_count': post.bookmarks.count()})
    return JsonResponse({'error': 'POST request required'}, status=400)

@login_required
def follow_toggle(request, username):
    if request.method == 'POST':
        target_user = get_object_or_404(User, username=username)
        follower = request.user
        if follower == target_user:
            return JsonResponse({'error': 'You cannot follow yourself'}, status=400)
            
        follow_rel = Follow.objects.filter(follower=follower, following=target_user)
        if follow_rel.exists():
            follow_rel.delete()
            following = False
        else:
            Follow.objects.create(follower=follower, following=target_user)
            following = True
            # Notify target
            Notification.objects.create(
                recipient=target_user,
                sender=follower,
                notification_type='follow',
                text=f"{follower.username} started following you!"
            )
        followers_count = Follow.objects.filter(following=target_user).count()
        return JsonResponse({'following': following, 'followers_count': followers_count})
    return JsonResponse({'error': 'POST request required'}, status=400)

@login_required
def bookmarks_dashboard(request):
    bookmarked_posts = request.user.bookmarked_posts.all().order_by('-created_at')
    paginator = Paginator(bookmarked_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'bookmarks.html', {'page_obj': page_obj})

# Notifications Lists
@login_required
def notifications_list(request):
    notifications = request.user.notifications.all()
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def notifications_read_all(request):
    if request.method == 'POST':
        request.user.notifications.filter(is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'POST request required'}, status=400)

# Custom Admin Analytics Dashboard
@login_required
def custom_admin_dashboard(request):
    if not request.user.is_superuser and not getattr(request.user.profile, 'is_moderator', False):
        return redirect('home')

    # Metrics
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_views = sum(p.views_count for p in Post.objects.all())
    active_sessions = LoginActivityLog.objects.filter(is_success=True).values('user').distinct().count()

    # Data aggregates for Chart.js
    categories_data = list(Post.objects.values('category').annotate(count=Count('id')))
    categories_labels = [c['category'] for c in categories_data]
    categories_counts = [c['count'] for c in categories_data]

    # Audit Logs
    login_logs = LoginActivityLog.objects.order_by('-timestamp')[:20]
    all_users = User.objects.all().order_by('-date_joined')
    all_posts = Post.objects.all().order_by('-created_at')
    all_comments = Comment.objects.all().order_by('-created_at')

    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_views': total_views,
        'active_sessions': active_sessions,
        'categories_labels': categories_labels,
        'categories_counts': categories_counts,
        'login_logs': login_logs,
        'all_users': all_users,
        'all_posts': all_posts,
        'all_comments': all_comments
    })

@login_required
def admin_user_ban(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')
    target_user = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=target_user)
    profile.is_banned = not profile.is_banned
    profile.save()
    
    # Deactivate login status if banned
    target_user.is_active = not profile.is_banned
    target_user.save()
    
    return redirect('admin_dashboard')

@login_required
def admin_post_approve(request, post_id):
    if not request.user.is_superuser and not request.user.profile.is_moderator:
        return redirect('home')
    post = get_object_or_404(Post, id=post_id)
    post.is_draft = not post.is_draft  # Simple draft/published toggle
    post.save()
    return redirect('admin_dashboard')

@login_required
def admin_comment_moderate(request, comment_id):
    if not request.user.is_superuser and not request.user.profile.is_moderator:
        return redirect('home')
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = not comment.is_approved
    comment.save()
    return redirect('admin_dashboard')

@login_required
def admin_site_settings(request):
    if not request.user.is_superuser:
        return redirect('home')
    site_config, _ = SiteSetting.objects.get_or_create(id=1)
    if request.method == 'POST':
        site_config.site_title = request.POST.get('site_title', 'Campus Thoughts')
        site_config.footer_text = request.POST.get('footer_text', '')
        site_config.maintenance_mode = request.POST.get('maintenance_mode') == 'on'
        site_config.save()
        return redirect('admin_dashboard')
    return render(request, 'admin_settings.html', {'site_config': site_config})

@login_required
def admin_login_logs(request):
    if not request.user.is_superuser:
        return redirect('home')
    logs = LoginActivityLog.objects.order_by('-timestamp')
    paginator = Paginator(logs, 30)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'admin_logs.html', {'page_obj': page_obj})

# ==============================================================================
# SECURE PASSWORD RECOVERY & ACCOUNT SECURITY VIEWS
# ==============================================================================
from django.contrib import messages
from django.utils import timezone
from .forms import ForgotPasswordRequestForm, OTPVerificationForm, ResetPasswordSecureForm
from .models import OTPVerification
from .utils import generate_secure_otp, send_secure_reset_email, invalidate_user_sessions_and_jwt

def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = ForgotPasswordRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email__iexact=email)
                
                # Rate limit OTP generation (prevent spamming: max 1 per 60 seconds)
                one_minute_ago = timezone.now() - timezone.timedelta(seconds=60)
                recent_otp = OTPVerification.objects.filter(user=user, created_at__gt=one_minute_ago)
                if recent_otp.exists():
                    messages.error(request, "Please wait at least 60 seconds before requesting another recovery code.")
                    return render(request, 'registration/forgot_password.html', {'form': form})
                    
                # Create OTP and send security email
                otp_record = generate_secure_otp(user)
                send_secure_reset_email(user, otp_code=otp_record.otp_code)
            except User.DoesNotExist:
                # Do nothing if user doesn't exist to prevent enumeration
                pass
            except Exception as e:
                messages.error(request, f"An error occurred while sending the email: {str(e)}")
                return render(request, 'registration/forgot_password.html', {'form': form})
            
            # Always show success and redirect, whether user exists or not
            request.session['reset_email'] = email
            messages.success(request, "A secure 6-digit OTP verification code has been dispatched to your email address.")
            return redirect('verify_otp')
    else:
        form = ForgotPasswordRequestForm()
        
    return render(request, 'registration/forgot_password.html', {'form': form})

def verify_otp(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    email = request.session.get('reset_email')
    if not email:
        messages.error(request, "Invalid access. Please enter your email to start the recovery flow.")
        return redirect('forgot_password')
        
    user = get_object_or_404(User, email__iexact=email)
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            otp_input = form.cleaned_data['otp_code']
            
            # Fetch active OTP records
            otp_records = OTPVerification.objects.filter(user=user, is_verified=False, expires_at__gt=timezone.now()).order_by('-created_at')
            if not otp_records.exists():
                messages.error(request, "Your verification code has expired or is invalid. Please request a new one.")
                return redirect('forgot_password')
                
            active_otp = otp_records.first()
            
            # Check maximum verification attempts to block brute-forcing
            if active_otp.attempts >= 3:
                active_otp.is_verified = True  # Mark as verified/used to destroy it
                active_otp.save()
                messages.error(request, "Maximum verification attempts exceeded. Please request a new recovery code.")
                return redirect('forgot_password')
                
            if active_otp.otp_code == otp_input:
                active_otp.is_verified = True
                active_otp.save()
                request.session['otp_verified'] = True
                messages.success(request, "OTP verification successful. You can now configure your new password.")
                return redirect('reset_password')
            else:
                active_otp.attempts += 1
                active_otp.save()
                attempts_left = 3 - active_otp.attempts
                messages.error(request, f"Incorrect verification code. You have {attempts_left} attempt(s) remaining.")
    else:
        form = OTPVerificationForm()
        
    return render(request, 'registration/verify_otp.html', {'form': form, 'email': email})

def reset_password(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified')
    
    if not email or not otp_verified:
        messages.error(request, "Session expired or invalid. Please verify your email again.")
        return redirect('forgot_password')
        
    user = get_object_or_404(User, email__iexact=email)
    
    if request.method == 'POST':
        form = ResetPasswordSecureForm(request.POST, user=user)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            
            # Invalidate other browser sessions & SimpleJWT tokens immediately
            invalidate_user_sessions_and_jwt(user)
            
            # Clear recovery parameters from session
            request.session.pop('reset_email', None)
            request.session.pop('otp_verified', None)
            
            messages.success(request, "Password reset successful! All other active sessions have been signed out. Please sign in now.")
            return redirect('login')
    else:
        form = ResetPasswordSecureForm(user=user)
        
    return render(request, 'registration/reset_password.html', {'form': form})