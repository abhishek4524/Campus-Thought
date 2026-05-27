import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusThoughts.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

User.objects.filter(username='testuser5').delete()
u = User.objects.create_user('testuser5', 'test5@test.com', 'pass123')
c = Client()
assert c.login(username='testuser5', password='pass123')
output = BytesIO()
img = Image.new('RGB', (1, 1), color='blue')
img.save(output, format='PNG')
output.seek(0)
image = SimpleUploadedFile('test.png', output.read(), content_type='image/png')
response = c.post('/create/', {'text': 'Image Test', 'description': 'Has image', 'category': 'Programming', 'photo': image}, SERVER_NAME='127.0.0.1', SERVER_PORT='8000')
print('status', response.status_code)
print('redir', response.get('Location'))
full_response = c.get(response.get('Location'), SERVER_NAME='127.0.0.1', SERVER_PORT='8000')
content = full_response.content.decode('utf-8', errors='replace')
print('full status', full_response.status_code)
print('found featured banner', 'Featured Banner Image' in content)
print('found img tag', '<img src="' in content)
print('image block snippet')
idx = content.find('Featured Banner Image')
if idx != -1:
    print(content[idx:idx+800])
else:
    idx2 = content.find('<img src="')
    print('first img idx', idx2)
    print(content[idx2:idx2+800] if idx2 != -1 else 'no img tag')
