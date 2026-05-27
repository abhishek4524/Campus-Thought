import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusThoughts.settings')
django.setup()
from django.test import RequestFactory
from django.contrib.auth.models import User
from blog.views import BlogAutosaveView

user = User.objects.first()
print('user', user)
if not user:
    raise SystemExit('No user found')

factory = RequestFactory()
request = factory.post('/autosave/', {
    'text': 'Test autosave',
    'description': 'Hello world',
    'category': 'Programming',
    'is_draft': 'on',
    'seo_title': 'Test',
    'seo_description': 'Desc',
})
request.user = user
request._dont_enforce_csrf_checks = True

response = BlogAutosaveView.as_view()(request)
print('status', response.status_code)
print('content', response.content.decode('utf-8', 'replace'))
try:
    print('json', response.json())
except Exception as exc:
    print('json error', exc)
