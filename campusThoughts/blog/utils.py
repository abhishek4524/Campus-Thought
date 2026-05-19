import secrets
import string
from django.utils import timezone
from datetime import timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import OTPVerification
from django.contrib.sessions.models import Session
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

def generate_secure_otp(user):
    """
    Generates a secure 6-digit OTP code using cryptographic choice,
    expiring exactly in 5 minutes.
    """
    digits = string.digits
    otp_code = "".join(secrets.choice(digits) for _ in range(6))
    
    # Define expiry (5 minutes from now)
    expires_at = timezone.now() + timedelta(minutes=5)
    
    # Store verification log
    otp_record = OTPVerification.objects.create(
        user=user,
        email=user.email,
        otp_code=otp_code,
        expires_at=expires_at
    )
    return otp_record

def send_secure_reset_email(user, reset_url=None, otp_code=None):
    """
    Dispatches a highly premium HTML email containing both OTP codes
    and secure reset links with explicit anti-phishing notices and plain text fallbacks.
    """
    subject = "🔑 Campus Thoughts - Secure Password Recovery Request"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'security@campusthoughts.edu')
    to_email = user.email
    
    # Context dictionary for templates
    context = {
        'username': user.username,
        'reset_url': reset_url,
        'otp_code': otp_code,
        'expires_minutes': 5 if otp_code else 15,
        'support_email': 'support@campusthoughts.edu',
    }
    
    # Render premium HTML content and plain text fallback
    html_content = render_to_string('registration/password_reset_email.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    email.send(fail_silently=False)

def invalidate_user_sessions_and_jwt(user):
    """
    Invalidates all browser session keys and SimpleJWT refresh tokens associated
    with the target user to block unauthorized hijacked connections instantly.
    """
    # 1. Invalidate Django session IDs
    sessions = Session.objects.all()
    for session in sessions:
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id):
            session.delete()
            
    # 2. Blacklist all outstanding JWT refresh tokens for SimpleJWT
    try:
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            # Check if not already blacklisted to prevent integrity issues
            if not BlacklistedToken.objects.filter(token=token).exists():
                BlacklistedToken.objects.create(token=token)
    except Exception as e:
        # Gracefully handle simplejwt blacklist table mismatches if not fully installed
        print("SimpleJWT Blacklist Invalidation notice:", e)
