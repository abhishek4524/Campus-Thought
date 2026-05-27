#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusThoughts.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from blog.models import Post
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

# Clean up
User.objects.filter(username='testdraft2').delete()
user = User.objects.create_user(username='testdraft2', password='pass', email='test@test.com')

# Create test image as SimpleUploadedFile
img = Image.new('RGB', (100, 100), color='red')
img_io = BytesIO()
img.save(img_io, format='PNG')
img_io.seek(0)

uploaded_file = SimpleUploadedFile(
    name='test_draft.png',
    content=img_io.read(),
    content_type='image/png'
)

# Step 1: Create draft post with image
client = Client(enforce_csrf_checks=False)
client.login(username='testdraft2', password='pass')

response = client.post('/autosave/', {
    'text': 'Draft Test Article',
    'description': '<p>This is draft content</p>',
    'category': 'Programming',
    'photo': uploaded_file
})

print('=== AUTOSAVE TEST ===')
print(f'Status: {response.status_code}')

data = {}
try:
    data = response.json()
except:
    print(f'Error: {response.content.decode("utf-8")[:200]}')

print(f'Success: {data.get("success")}')

if data.get('success'):
    draft_id = data.get('post_id')
    print(f'✓ Draft ID: {draft_id}')
    
    draft = Post.objects.get(id=draft_id)
    print(f'✓ Draft is_draft: {draft.is_draft}')
    print(f'✓ Draft has photo: {bool(draft.photo)}')
    
    # Test recovery page
    print('\n=== RECOVERY PAGE TEST ===')
    recovery_response = client.get(f'/create/?post_id={draft_id}')
    print(f'Status: {recovery_response.status_code}')
    html = recovery_response.content.decode('utf-8')
    print(f'Has existing-photo: {"existing-photo" in html}')
    print(f'Has draft title: {"Draft Test Article" in html}')
    
    # Publish
    print('\n=== PUBLISH TEST ===')
    pub_resp = client.post('/create/', {
        'text': 'Published Version',
        'description': '<p>Published content</p>',
        'category': 'Programming',
        'is_draft': False,
        'post_id': draft_id
    })
    print(f'Status: {pub_resp.status_code}')
    
    published = Post.objects.get(id=draft_id)
    print(f'✓ Published is_draft: {published.is_draft}')
    print(f'✓ Published has photo: {bool(published.photo)}')
    
    # Check final view
    print('\n=== FINAL VIEW TEST ===')
    final = client.get(f'/post/{published.slug}/')
    print(f'Status: {final.status_code}')
    final_html = final.content.decode('utf-8')
    print(f'Has Featured Banner: {"Featured Banner Image" in final_html}')
    if '/media/photos/' in final_html:
        # Extract image URL
        import re
        match = re.search(r'src="(/media/photos/[^"]+)"', final_html)
        if match:
            print(f'✓ Image URL: {match.group(1)}')
    
else:
    print('✗ Autosave failed')
