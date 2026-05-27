import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusThoughts.settings')
django.setup()
from django.test import Client
from django.contrib.auth.models import User

user = User.objects.first()
print('user', user)
if not user:
    raise SystemExit('No user available to test autosave')

client = Client()
client.force_login(user)

resp = client.post('/autosave/', {
    'text': 'Test autosave',
    'description': 'Hello world',
    'category': 'Programming',
    'is_draft': 'on',
    'seo_title': 'Test',
    'seo_description': 'Desc',
})
print('status', resp.status_code)
print('content', resp.content.decode('utf-8', 'replace'))
try:
    print('json', resp.json())
except Exception as exc:
    print('json parse error', exc)
