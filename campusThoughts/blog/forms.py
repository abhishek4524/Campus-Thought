from django import forms
from .models import Post, Comment, Profile
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ckeditor.widgets import CKEditorWidget

class BlogForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'description', 'photo', 'category', 'is_draft', 'seo_title', 'seo_description']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'Enter a catchy title for your campus thoughts...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition'
            }),
            'is_draft': forms.CheckboxInput(attrs={
                'class': 'rounded border-slate-300 dark:border-slate-700 text-blue-600 focus:ring-blue-500'
            }),
            'seo_title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'SEO Optimized Title (defaults to post title)'
            }),
            'seo_description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'Short summary for search engine results...',
                'rows': 3
            })
        }
    
    description = forms.CharField(widget=CKEditorWidget(attrs={
        'placeholder': 'Write your thoughts here...'
    }))
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_text']
        widgets = {
            'comment_text': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'Join the discussion... write a constructive comment!',
                'rows': 3
            })
        }
        
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
        'placeholder': 'email@campus.edu'
    }))
    
    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'email':
                self.fields[field].widget.attrs.update({
                    'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition'
                })

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'banner', 'bio', 'website', 'github', 'linkedin', 'twitter']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'Tell us about yourself, your major, interests...',
                'rows': 4
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'https://mywebsite.com'
            }),
            'github': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'https://github.com/username'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'https://linkedin.com/in/username'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
                'placeholder': 'https://twitter.com/username'
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            }),
            'banner': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'
            })
        }

class ForgotPasswordRequestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full px-4 py-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition text-sm',
        'placeholder': 'Enter your campus email address'
    }))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("No account is associated with this email address.")
        return email

class OTPVerificationForm(forms.Form):
    otp_code = forms.CharField(max_length=6, min_length=6, widget=forms.TextInput(attrs={
        'class': 'w-full text-center tracking-[0.75em] font-black text-xl px-4 py-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition',
        'placeholder': '••••••'
    }))

class ResetPasswordSecureForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition text-sm',
        'placeholder': 'Enter a strong new password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full px-4 py-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-blue-500 outline-none transition text-sm',
        'placeholder': 'Confirm your new password'
    }))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        
        # 1. Length Check
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
            
        # 2. Character Set Checks
        import re
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter (A-Z).")
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter (a-z).")
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("Password must contain at least one number (0-9).")
        if not re.search(r'[^a-zA-Z0-9]', password):
            raise forms.ValidationError("Password must contain at least one special character (e.g. !@#$%).")
            
        # 3. User similarity
        if self.user:
            from django.utils.text import slugify
            username_slug = slugify(self.user.username)
            if username_slug in password.lower() or self.user.username.lower() in password.lower():
                raise forms.ValidationError("Password is too similar to your username.")
            if self.user.email and self.user.email.split('@')[0].lower() in password.lower():
                raise forms.ValidationError("Password cannot contain parts of your email address.")

        # 4. Common passwords blacklist
        common_passwords = ['password', '12345678', 'qwertyuiop', 'campus123', 'campusthoughts', 'password123']
        if password.lower() in common_passwords:
            raise forms.ValidationError("This password is too common or easy to guess.")

        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('new_password')
        confirm = cleaned_data.get('confirm_password')

        if password and confirm and password != confirm:
            self.add_error('confirm_password', "Passwords do not match.")
