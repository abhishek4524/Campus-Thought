import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusThoughts.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

User.objects.filter(username='testuser3').delete()
u = User.objects.create_user('testuser3', 'test3@test.com', 'pass123')
c = Client()
assert c.login(username='testuser3', password='pass123')
image = SimpleUploadedFile(
    'test.png',
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x01\x00\x00\x05\x00\x01\x0d\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82',
    content_type='image/png'
)
response = c.post(
    '/create/',
    {'text': 'Image Test', 'description': 'Has image', 'category': 'Programming', 'photo': image},
    SERVER_NAME='127.0.0.1',
    SERVER_PORT='8000'
)
content = response.content.decode('utf-8', errors='replace')
print('status', response.status_code)
print('redir', response.get('Location'))
print('has context attr', hasattr(response, 'context'))
print('context repr', repr(response.context) if hasattr(response, 'context') else 'no context')
print('error block present', 'Please fix these items before saving' in content)
for msg in ['Upload cannot exceed 6 MB.', 'Only JPEG, PNG, and WEBP files are allowed.', 'A headline is required.', 'SEO title must be 140 characters or fewer.', 'Meta description must be 160 characters or fewer.']:
    print(msg, msg in content)
print('snippet:', content[content.find('Please fix these items before saving')-200:content.find('Please fix these items before saving')+1200] if 'Please fix these items before saving' in content else content[:2000])
