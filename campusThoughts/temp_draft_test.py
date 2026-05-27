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

# Create test user
User.objects.filter(username='testdraft').delete()
user = User.objects.create_user(username='testdraft', password='pass', email='test@test.com')

# Create test image
img = Image.new('RGB', (100, 100), color='red')
img_io = BytesIO()
img.save(img_io, format='PNG')
img_io.seek(0)
img_io.name = 'test_draft.png'

# Step 1: Create draft post with image
client = Client(enforce_csrf_checks=False)
client.login(username='testdraft', password='pass')

# First, directly test without follow
response = client.post('/autosave/', {
    'text': 'Draft Test Article',
    'description': '<p>This is draft content</p>',
    'category': 'Programming',
    'photo': img_io
})

print('Autosave response:', response.status_code)
print('Response content type:', response.get('content-type', 'unknown'))

# Try to parse response
data = {}
try:
    data = response.json()
except:
    if response.status_code >= 400:
        print('Error response body:', response.content.decode('utf-8')[:500])
    data = {}
print('Autosave result:', data)

if data.get('success'):
    draft_id = data.get('post_id')
    print(f'\nDraft created with ID: {draft_id}')
    
    # Verify draft exists in DB
    draft = Post.objects.get(id=draft_id)
    print(f'Draft is_draft: {draft.is_draft}')
    print(f'Draft photo: {draft.photo}')
    print(f'Draft photo URL: {draft.photo.url if draft.photo else "None"}')
    
    # Step 2: Verify URL includes post_id for recovery
    print(f'\nDraft recovery URL: /create/?post_id={draft_id}')
    
    # Step 3: Simulate recovery - fetch the create page with post_id
    recovery_response = client.get(f'/create/?post_id={draft_id}')
    print(f'Recovery page status: {recovery_response.status_code}')
    
    # Check if existing photo is displayed
    if 'existing-photo' in recovery_response.content.decode('utf-8'):
        print('✓ Existing photo block found in recovery page')
    else:
        print('✗ Existing photo block NOT found in recovery page')
    
    if 'Draft Test Article' in recovery_response.content.decode('utf-8'):
        print('✓ Draft text found in recovery page')
    else:
        print('✗ Draft text NOT found in recovery page')
    
    # Step 4: Continue editing and publish
    img2 = Image.new('RGB', (100, 100), color='blue')
    img_io2 = BytesIO()
    img2.save(img_io2, format='PNG')
    img_io2.seek(0)
    img_io2.name = 'test_draft_updated.png'
    
    publish_response = client.post('/create/', {
        'text': 'Draft Test Article Published',
        'description': '<p>This is published content</p>',
        'category': 'Programming',
        'is_draft': False,
        'photo': img_io2,
        'post_id': draft_id
    }, follow=False)
    
    print(f'\nPublish response: {publish_response.status_code}')
    
    if publish_response.status_code == 302:
        # Check if post was published
        published = Post.objects.get(id=draft_id)
        print(f'Published is_draft: {published.is_draft}')
        print(f'Published photo: {published.photo}')
        print(f'Published URL: {publish_response.url}')
    
    # Step 5: Verify published post displays image
    final_response = client.get(f'/post/{published.slug}/')
    print(f'\nPublished post status: {final_response.status_code}')
    
    html = final_response.content.decode('utf-8')
    if 'object-cover' in html and 'Featured Banner Image' in html:
        print('✓ Published post includes featured image block')
        if 'src="/media/photos/' in html or 'src="http' in html:
            print('✓ Image src attribute found')
        else:
            print('✗ Image src attribute NOT found')
    else:
        print('✗ Published post missing featured image block')
