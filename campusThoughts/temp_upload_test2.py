import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusThoughts.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from blog.models import Post
from io import BytesIO
from PIL import Image

User.objects.filter(username='testuser4').delete()
u = User.objects.create_user('testuser4', 'test4@test.com', 'pass123')
c = Client()
assert c.login(username='testuser4', password='pass123')
output = BytesIO()
img = Image.new('RGB', (1, 1), color='blue')
img.save(output, format='PNG')
output.seek(0)
image = SimpleUploadedFile('test.png', output.read(), content_type='image/png')
response = c.post(
    '/create/',
    {'text': 'Image Test', 'description': 'Has image', 'category': 'Programming', 'photo': image},
    SERVER_NAME='127.0.0.1',
    SERVER_PORT='8000'
)
print('status', response.status_code)
print('redir', response.get('Location'))
content = response.content.decode('utf-8', errors='replace')
print('error present', 'Please fix these items before saving' in content)
print('photo validation error', 'Upload a valid image' in content)
print('photo invalid message', 'Upload a valid image' in content or 'not an image' in content)
if 'Please fix these items before saving' in content:
    idx = content.find('Please fix these items before saving')
    print(content[idx:idx+1200])

posts = Post.objects.filter(user=u)
print('post count', posts.count())
if posts.exists():
    p = posts.latest('id')
    print('photo field', p.photo)
    try:
        print('photo url', p.photo.url)
    except Exception as e:
        print('photo url error', e)

full_response = c.get(f'/post/{response.get("Location").split("/post/")[-1]}', SERVER_NAME='127.0.0.1', SERVER_PORT='8000')
print('full blog status', full_response.status_code)
print('full blog image present', '/media/photos/test.png' in full_response.content.decode('utf-8', errors='replace'))
print('full blog snippet', full_response.content.decode('utf-8', errors='replace')[:800])
