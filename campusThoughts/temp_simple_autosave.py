#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusThoughts.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

# Clean up
User.objects.filter(username='testdraft3').delete()
user = User.objects.create_user(username='testdraft3', password='pass', email='test@test.com')

client = Client(enforce_csrf_checks=False)
print('Login result:', client.login(username='testdraft3', password='pass'))

# Get CSRF token first
get_resp = client.get('/create/')
csrf_token = get_token(client.get('/create/').wsgi_request) if hasattr(client.get('/create/'), 'wsgi_request') else None

print(f'CSRF token: {csrf_token}')

# Try POST with CSRF token
response = client.post('/autosave/', {
    'text': 'Test',
    'description': '<p>Test</p>',
    'category': 'Programming',
}, HTTP_X_CSRFTOKEN=csrf_token)

print(f'\nAutosave with token:')
print(f'Status: {response.status_code}')
if response.status_code == 400:
    print(f'Response: {response.content.decode("utf-8")[:300]}')
else:
    try:
        print(f'JSON: {response.json()}')
    except Exception as e:
        print(f'Error parsing: {e}')

