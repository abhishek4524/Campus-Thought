#!/usr/bin/env python
import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campusThoughts.settings')
django.setup()

from blog.forms import BlogForm
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile

# Get or create test user
user, _ = User.objects.get_or_create(username='testdraft', defaults={'email': 'test@test.com', 'password': 'pass'})

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

# Test the form directly
data = {
    'text': 'Draft Test Article',
    'description': '<p>This is draft content</p>',
    'category': 'Programming',
}

files = {
    'photo': uploaded_file
}

form = BlogForm(data, files)
print('Form is valid:', form.is_valid())

if not form.is_valid():
    print('Form errors:', form.errors)
    for field, errors in form.errors.items():
        print(f'  {field}: {errors}')
else:
    print('Form is valid! ✓')
    
# Test without photo
print('\n--- Test without photo ---')
form2 = BlogForm(data, {})
print('Form is valid (no photo):', form2.is_valid())
if not form2.is_valid():
    print('Form errors:', form2.errors)


